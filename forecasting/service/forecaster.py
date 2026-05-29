import pandas as pd
from abc import ABC, abstractmethod
from datetime import date, timedelta
from typing import List
from statsmodels.tsa.statespace.sarimax import SARIMAX
from domain.models import CurrencyRate, ForecastPoint

# ─────────────────────────────────────────────
# ПАТТЕРН: Strategy (Стратегия)
#
# Базовый класс определяет интерфейс прогноза.
# Конкретные алгоритмы (SARIMAX, ARIMA и т.д.)
# реализуют его независимо друг от друга.
#
# ForecastService не знает КАКОЙ алгоритм используется —
# он просто вызывает predict(). Алгоритм можно
# поменять без изменения остального кода.
# ─────────────────────────────────────────────

class BaseForecast(ABC):
    """
    Абстрактная стратегия прогнозирования.
    Любой алгоритм прогноза должен реализовать predict().
    """

    @abstractmethod
    def predict(
        self,
        rates: List[CurrencyRate],
        days: int
    ) -> List[ForecastPoint]:
        """
        Принимает историю курсов, возвращает прогноз на N дней.
        """
        ...


class SARIMAXForecaster(BaseForecast):
    """
    Конкретная стратегия: прогноз через SARIMAX.

    SARIMAX — модель временных рядов с:
    - AR (авторегрессия): зависимость от прошлых значений
    - I (интегрирование): убирает тренд
    - MA (скользящее среднее): сглаживает шум
    - X (экзогенные переменные): внешние факторы (не используем)

    order=(1,1,1) — базовые параметры ARIMA
    seasonal_order=(1,1,1,5) — недельная сезонность (5 рабочих дней)
    """

    def __init__(
        self,
        order: tuple = (1, 1, 1),
        seasonal_order: tuple = (1, 1, 1, 5)
    ):
        # Параметры модели сохраняем при инициализации —
        # это инкапсуляция конфигурации внутри класса
        self.order = order
        self.seasonal_order = seasonal_order

    def predict(
        self,
        rates: List[CurrencyRate],
        days: int
    ) -> List[ForecastPoint]:
        """
        Обучает модель на истории и возвращает прогноз.

        Шаги:
        1. Преобразуем список CurrencyRate в pandas Series
        2. Обучаем SARIMAX модель
        3. Делаем прогноз на N шагов вперёд
        4. Преобразуем результат в список ForecastPoint
        """
        # Шаг 1: строим временной ряд из истории курсов
        # pandas Series с датой в качестве индекса —
        # именно такой формат нужен SARIMAX
        series = pd.Series(
            data=[r.rate for r in rates],
            index=pd.DatetimeIndex([r.date for r in rates]),
            name="rate"
        )

        # Шаг 2: создаём и обучаем модель
        # disp=False — отключаем вывод итераций обучения в консоль
        model = SARIMAX(
            series,
            order=self.order,
            seasonal_order=self.seasonal_order
        )
        result = model.fit(disp=False)

        forecast_res = result.get_forecast(steps=days)
        predictions = forecast_res.predicted_mean
        conf_int = forecast_res.conf_int(alpha=0.2)

        last_date = rates[-1].date
        points: list[ForecastPoint] = []
        for i, val in enumerate(predictions):
            lower = upper = None
            if conf_int is not None and len(conf_int) > i:
                lower = round(float(conf_int.iloc[i, 0]), 4)
                upper = round(float(conf_int.iloc[i, 1]), 4)
            points.append(
                ForecastPoint(
                    date=last_date + timedelta(days=i + 1),
                    predicted_value=round(float(val), 4),
                    lower=lower,
                    upper=upper,
                )
            )
        return points