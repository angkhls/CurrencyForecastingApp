from datetime import date, timedelta
from typing import Dict, List, Optional

from domain.models import (
    ChartData,
    ConvertResult,
    CurrencyCode,
    CurrencyPair,
    CurrencyRate,
    DashboardRate,
    DashboardResponse,
    ForecastMethod,
    ForecastResult,
    MacroPanel,
    ModelMetrics,
    PeriodPreset,
)
from domain.repositories import CurrencyRateRepository
from infrastructure.nbrb_client import NbrbApiClient
from service.forecaster import BaseForecast, SARIMAXForecaster
from service.gemini_forecaster import GeminiForecaster
from service.metrics_calc import mape, rmse
from service.calendar_utils import (
    compute_y_domain,
    count_weekdays_after,
    expand_forecast_to_calendar,
    filter_weekdays,
)
from service.macro_service import MacroService
from service.pairs import build_pair_series, pair_currencies, period_to_days
from service.technical import build_chart_points

HISTORY_DAYS = 365
HOLDOUT_DAYS = 30
DASHBOARD_CURRENCIES: List[CurrencyCode] = ["USD", "EUR", "RUB", "CNY"]


class RateService:
    def __init__(
        self,
        repository: CurrencyRateRepository,
        nbrb_client: NbrbApiClient,
        gemini_api_key: str = "",
        gemini_model: str = "gemini-2.0-flash",
    ):
        self._repo = repository
        self._nbrb = nbrb_client
        self._gemini_key = gemini_api_key
        self._gemini_model = gemini_model
        self._sarimax = SARIMAXForecaster()
        self._macro = MacroService()

    def _forecaster(self, method: ForecastMethod) -> BaseForecast:
        if method == "gemini":
            return GeminiForecaster(self._gemini_key, self._gemini_model)
        return self._sarimax

    async def sync_rates(self, currency: CurrencyCode) -> int:
        latest = await self._repo.get_latest(currency)
        today = date.today()

        if latest is None:
            from_date = today - timedelta(days=HISTORY_DAYS)
        elif latest.date >= today:
            return 0
        else:
            from_date = latest.date + timedelta(days=1)

        rates = await self._nbrb.get_rates_for_period(currency, from_date, today)
        if rates:
            await self._repo.save_many(rates)
        return len(rates)

    async def _ensure_currency(self, currency: CurrencyCode) -> None:
        await self.sync_rates(currency)

    async def _load_pair_history(self, pair: CurrencyPair, days: int) -> List[CurrencyRate]:
        base, cross = pair_currencies(pair)
        await self._ensure_currency(base)
        if cross:
            await self._ensure_currency(cross)
        else:
            cross = "USD" if base != "USD" else "EUR"

        to_date = date.today()
        from_date = to_date - timedelta(days=days)
        base_hist = await self._repo.get_history(base, from_date, to_date)

        if pair in ("USD_BYN", "EUR_BYN"):
            return base_hist

        await self._ensure_currency("USD")
        usd_hist = await self._repo.get_history("USD", from_date, to_date)
        if pair == "EUR_USD":
            eur_hist = base_hist if base == "EUR" else await self._repo.get_history("EUR", from_date, to_date)
            return build_pair_series(pair, usd_hist, eur_hist)
        return base_hist

    async def get_history(
        self, currency: CurrencyCode, days: int = 30
    ) -> List[CurrencyRate]:
        await self._ensure_currency(currency)
        to_date = date.today()
        from_date = to_date - timedelta(days=days)
        return await self._repo.get_history(currency, from_date, to_date)

    async def get_rate_on_date(
        self, currency: CurrencyCode, target_date: date
    ) -> CurrencyRate:
        cached = await self._repo.get_by_currency_and_date(currency, target_date)
        if cached:
            return cached
        rate = await self._nbrb.get_rate(currency, target_date)
        await self._repo.save(rate)
        return rate

    async def get_latest_rate(self, currency: CurrencyCode) -> CurrencyRate:
        await self._ensure_currency(currency)
        latest = await self._repo.get_latest(currency)
        if latest is None:
            raise ValueError(f"Нет данных для валюты {currency}")
        return latest

    async def get_dashboard(self) -> DashboardResponse:
        rates: List[DashboardRate] = []
        for currency in DASHBOARD_CURRENCIES:
            try:
                latest = await self.get_latest_rate(currency)
                prev = await self._repo.get_by_currency_and_date(
                    currency, latest.date - timedelta(days=7)
                )
                change_pct = None
                if prev and prev.rate:
                    change_pct = round((latest.rate - prev.rate) / prev.rate * 100, 2)
                rates.append(
                    DashboardRate(
                        currency=currency,
                        rate=latest.rate,
                        date=latest.date,
                        change_pct=change_pct,
                    )
                )
            except ValueError:
                continue
        return DashboardResponse(rates=rates)

    async def convert(
        self, amount: float, from_currency: CurrencyCode, to_currency: CurrencyCode
    ) -> ConvertResult:
        if from_currency == to_currency:
            latest = await self.get_latest_rate(from_currency)
            return ConvertResult(
                amount=amount,
                from_currency=from_currency,
                to_currency=to_currency,
                rate=1.0,
                result=amount,
                date=latest.date,
            )

        from_rate = await self.get_latest_rate(from_currency)
        to_rate = await self.get_latest_rate(to_currency)
        # Курсы НБРБ: BYN за 1 единицу валюты
        result = amount * (from_rate.rate / to_rate.rate)
        cross_rate = from_rate.rate / to_rate.rate
        return ConvertResult(
            amount=amount,
            from_currency=from_currency,
            to_currency=to_currency,
            rate=round(cross_rate, 6),
            result=round(result, 4),
            date=from_rate.date,
        )

    async def get_chart(self, pair: CurrencyPair, period: PeriodPreset) -> ChartData:
        days = period_to_days(period)
        history = filter_weekdays(await self._load_pair_history(pair, days))
        points, levels = build_chart_points(history)
        extras: list[float] = [levels.support, levels.resistance]
        for p in points:
            if p.sma_20 is not None:
                extras.append(p.sma_20)
            if p.ema_20 is not None:
                extras.append(p.ema_20)
        y_min, y_max = compute_y_domain([p.rate for p in points], extras=extras)
        return ChartData(
            pair=pair,
            period=period,
            points=points,
            levels=levels,
            y_min=y_min,
            y_max=y_max,
        )

    async def get_macro(self, pair: CurrencyPair) -> MacroPanel:
        return await self._macro.get_panel(pair)

    def _evaluate_holdout(
        self, history: List[CurrencyRate], method: ForecastMethod, holdout: int
    ) -> tuple[float, float]:
        if len(history) <= holdout + 10:
            holdout = max(5, len(history) // 4)
        train = history[:-holdout]
        test = history[-holdout:]
        try:
            predicted = self._forecaster(method).predict(train, holdout)
        except Exception:
            return 0.0, 0.0
        actual = [r.rate for r in test]
        pred = [p.predicted_value for p in predicted[: len(test)]]
        if len(pred) != len(actual):
            n = min(len(pred), len(actual))
            actual, pred = actual[:n], pred[:n]
        if not actual:
            return 0.0, 0.0
        return round(mape(actual, pred), 2), round(rmse(actual, pred), 4)

    async def get_forecast(
        self,
        pair: CurrencyPair,
        days: int = 7,
        method: ForecastMethod = "sarimax",
    ) -> ForecastResult:
        history = filter_weekdays(await self._load_pair_history(pair, HISTORY_DAYS))
        if len(history) < 30:
            raise ValueError(
                f"Недостаточно данных для прогноза: {len(history)} дней (нужно ≥30)"
            )

        mape_val, rmse_val = self._evaluate_holdout(history, method, HOLDOUT_DAYS)
        last_date = history[-1].date
        biz_steps = max(1, count_weekdays_after(last_date, days))
        business_forecast = self._forecaster(method).predict(history, biz_steps)
        forecast_points = expand_forecast_to_calendar(
            business_forecast, last_date, days
        )

        return ForecastResult(
            pair=pair,
            method=method,
            forecast=forecast_points,
            mape=mape_val,
            rmse=rmse_val,
        )

    async def get_metrics(
        self, pair: CurrencyPair, method: ForecastMethod, holdout_days: int = 30
    ) -> ModelMetrics:
        history = await self._load_pair_history(pair, HISTORY_DAYS)
        mape_val, rmse_val = self._evaluate_holdout(history, method, holdout_days)
        return ModelMetrics(
            pair=pair,
            method=method,
            mape=mape_val,
            rmse=rmse_val,
            holdout_days=holdout_days,
        )

    async def compare_methods(self, pair: CurrencyPair) -> Dict[str, ModelMetrics]:
        result: Dict[str, ModelMetrics] = {}
        for method in ("sarimax", "gemini"):
            try:
                result[method] = await self.get_metrics(pair, method)  # type: ignore[arg-type]
            except Exception:
                result[method] = ModelMetrics(
                    pair=pair,
                    method=method,  # type: ignore[arg-type]
                    mape=-1.0,
                    rmse=-1.0,
                    holdout_days=HOLDOUT_DAYS,
                )
        return result
