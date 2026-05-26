from pydantic import BaseModel
from datetime import date
from typing import List, Literal

#одна точка прогноза
class ForecastPoint(BaseModel):
    date: date
    predicted_value: float

#ответ апи
class ForecastResponse(BaseModel):
    currency: Literal["USD", "BYN", "EUR"]
    forecast: List[ForecastPoint]
