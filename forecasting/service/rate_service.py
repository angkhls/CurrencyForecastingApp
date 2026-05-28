from datetime import date, timedelta
from typing import List
from domain.models import CurrencyRate, CurrencyCode, ForecastResult, RateHistory
from domain.repositories import CurrencyRateRepository
from infrastructure.nbrb_client import NbrbApiClient
from service.forecaster import BaseForecast

# ─────────────────────────────────────────────
# ПАТТЕРН: Facade (Фасад) + DI (Внедрение зависимостей)
#
# RateService — фасад: скрывает сложность взаимодействия
# между репозиторием, NBRB клиентом и алгоритмом прогноза.
#
# Зависимости (репозиторий, клиент, forecaster) передаются
# через конструктор — это Dependency Injection.
# Сервис не создаёт их сам, что упрощает тестирование.
# ─────────────────────────────────────────────

# Сколько дней истории загружаем для обучения модели
HISTORY_DAYS = 365


class RateService:
    """
    Сервис управления курсами валют.
    Оркестрирует: загрузку с NBRB → сохранение в БД → прогноз.
    """

    def __init__(
        self,
        repository: CurrencyRateRepository,  # абстракция, не конкретный класс!
        nbrb_client: NbrbApiClient,
        forecaster: BaseForecast             # абстракция стратегии прогноза
    ):
        self._repo = repository
        self._nbrb = nbrb_client
        self._forecaster = forecaster

    async def sync_rates(self, currency: CurrencyCode) -> int:
        """
        Синхронизировать курсы с NBRB.

        Логика:
        - Если данных нет — загружаем последние HISTORY_DAYS дней
        - Если данные устарели — догружаем только недостающие дни
        - Если данные свежие — ничего не делаем

        Возвращает количество загруженных записей.
        """
        latest = await self._repo.get_latest(currency)
        today = date.today()

        if latest is None:
            # Данных нет совсем — загружаем всю историю
            from_date = today - timedelta(days=HISTORY_DAYS)
        elif latest.date >= today:
            # Данные уже актуальны
            return 0
        else:
            # Загружаем только то чего не хватает
            from_date = latest.date + timedelta(days=1)

        rates = await self._nbrb.get_rates_for_period(
            currency, from_date, today
        )

        if rates:
            await self._repo.save_many(rates)

        return len(rates)

    async def get_history(
        self,
        currency: CurrencyCode,
        days: int = 30
    ) -> List[CurrencyRate]:
        """
        Получить историю курсов за последние N дней.
        Сначала синхронизируем данные, потом отдаём из БД.
        """
        await self.sync_rates(currency)

        to_date = date.today()
        from_date = to_date - timedelta(days=days)

        return await self._repo.get_history(currency, from_date, to_date)

    async def get_forecast(
        self,
        currency: CurrencyCode,
        days: int = 7
    ) -> ForecastResult:
        """
        Построить прогноз курса на N дней вперёд.

        Шаги:
        1. Убедиться что данные актуальны (sync)
        2. Загрузить историю из БД для обучения
        3. Передать историю в алгоритм прогноза
        4. Вернуть результат
        """
        # Шаг 1: синхронизация
        await self.sync_rates(currency)

        # Шаг 2: берём историю для обучения модели
        to_date = date.today()
        from_date = to_date - timedelta(days=HISTORY_DAYS)
        history = await self._repo.get_history(currency, from_date, to_date)

        if len(history) < 30:
            raise ValueError(
                f"Недостаточно данных для прогноза: {len(history)} дней. "
                f"Нужно минимум 30."
            )

        # Шаг 3: запускаем алгоритм прогноза (Strategy)
        forecast_points = self._forecaster.predict(history, days)

        # Шаг 4: возвращаем результат
        return ForecastResult(
            currency=currency,
            forecast=forecast_points
        )

    async def get_latest_rate(
        self,
        currency: CurrencyCode
    ) -> CurrencyRate:
        """
        Получить актуальный курс валюты.
        """
        await self.sync_rates(currency)
        latest = await self._repo.get_latest(currency)

        if latest is None:
            raise ValueError(f"Нет данных для валюты {currency}")

        return latest