import json
import re
from datetime import timedelta
from typing import List

from domain.models import CurrencyRate, ForecastMethod, ForecastPoint
from service.forecaster import BaseForecast

try:
    import google.generativeai as genai
except ImportError:
    genai = None


class GeminiForecaster(BaseForecast):
    """Прогноз через Google Gemini API по промпту с историей курсов."""

    def __init__(self, api_key: str, model_name: str = "gemini-2.0-flash"):
        if not api_key:
            raise ValueError("GEMINI_API_KEY не задан. Добавьте ключ в .env")
        if genai is None:
            raise ImportError("Установите пакет: pip install google-generativeai")
        genai.configure(api_key=api_key)
        self._model = genai.GenerativeModel(model_name)

    def predict(self, rates: List[CurrencyRate], days: int) -> List[ForecastPoint]:
        history = [
            {"date": r.date.isoformat(), "rate": round(r.rate, 6)}
            for r in rates[-90:]
        ]
        last_date = rates[-1].date
        prompt = f"""Ты финансовый аналитик. По истории официальных курсов НБРБ спрогнозируй курс на следующие {days} дней.

История (последние точки):
{json.dumps(history, ensure_ascii=False)}

Верни ТОЛЬКО JSON-массив без markdown:
[{{"date": "YYYY-MM-DD", "predicted_value": число}}, ...]
Ровно {days} элементов, даты подряд после {last_date.isoformat()}.
Числа должны быть реалистичны относительно последних значений."""

        response = self._model.generate_content(prompt)
        text = response.text.strip()
        text = re.sub(r"^```json\s*|\s*```$", "", text, flags=re.MULTILINE).strip()
        data = json.loads(text)

        return [
            ForecastPoint(
                date=last_date + timedelta(days=i + 1),
                predicted_value=round(float(item["predicted_value"]), 4),
            )
            for i, item in enumerate(data[:days])
        ]

    @staticmethod
    def method_name() -> ForecastMethod:
        return "gemini"
