from statsmodels.tsa.statespace.sarimax import SARIMAX
from typing import List
from domain.models import ForecastPoint
from datetime import date, timedelta
import pandas


class SARIMAForecaster:
    def forecast(self, rates: List[float], days: int):
        series = pandas.Series(rates)
        model = SARIMAX(series, order=(1,1,1), seasonal_order=(0,0,0,0))
        result = model.fit(disp=False)
        predictions = result.forecast(steps=days)

        today = date.today()
        return [
            ForecastPoint(
                date=today + timedelta(days=i+1),
                predicted_value=round(float(val), 4)
            )
            for i, val in enumerate(predictions)
        ]