from pydantic import BaseModel
from datetime import date
from typing import List, Literal

# ─────────────────────────────────────────────
# СУЩНОСТИ (Entities) — описывают данные нашей
# предметной области. Не знают ничего о БД или API.
# ─────────────────────────────────────────────

# Поддерживаемые валюты
CurrencyCode = Literal["USD", "EUR", "RUB"]


class CurrencyRate(BaseModel):
    """
    Сущность: один курс валюты на конкретную дату.
    Это основная единица данных в системе.
    """
    currency: CurrencyCode   # код валюты (USD, EUR, RUB)
    date: date               # дата курса
    rate: float              # курс относительно BYN


class ForecastPoint(BaseModel):
    """
    Сущность: одна точка прогноза.
    Содержит предсказанный курс на будущую дату.
    """
    date: date               # дата прогноза
    predicted_value: float   # предсказанный курс


class ForecastResult(BaseModel):
    """
    Value Object: результат прогноза целиком.
    Объединяет список точек прогноза для одной валюты.
    Value Object — неизменяемый, идентифицируется
    по значению, а не по ID.
    """
    currency: CurrencyCode
    forecast: List[ForecastPoint]


class RateHistory(BaseModel):
    """
    Value Object: исторические данные по валюте.
    Используется для передачи истории курсов
    в сервис прогнозирования.
    """
    currency: CurrencyCode
    rates: List[CurrencyRate]