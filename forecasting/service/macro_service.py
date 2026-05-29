import asyncio
import xml.etree.ElementTree as ET
from datetime import date, timedelta
from typing import List, Optional

import httpx

from domain.models import CurrencyPair, MacroIndicator, MacroPanel

# Краткие пояснения для курсовой
IMPACT = {
    "cbr_rate": "Рост ставки ЦБ РФ обычно укрепляет рубль — вклады в RUB привлекательнее.",
    "nbrb_rate": "Ставка НБРБ влияет на спрос на BYN и кросс-курсы через дифференциал ставок.",
    "brent": "Для сырьевых экономик рост нефти часто поддерживает нац. валюту (больше экспортной выручки).",
    "gold": "Золото — индикатор «защитного» спроса; рост часто сопровождает напряжение на FX.",
    "cpi_ru": "Высокая инфляция на дистанции ослабляет покупательную способность валюты.",
}


class MacroService:
    """Макро-факторы: ставки, сырьё, инфляция (публичные источники)."""

    async def get_panel(self, pair: CurrencyPair) -> MacroPanel:
        cbr, nbrb, brent, gold, cpi = await asyncio.gather(
            self._fetch_cbr_key_rate(),
            self._fetch_nbrb_refinance(),
            self._fetch_yahoo_last("BZ=F", "Brent (нефть)"),
            self._fetch_yahoo_last("GC=F", "Золото"),
            self._fetch_cbr_inflation(),
            return_exceptions=True,
        )

        indicators: List[MacroIndicator] = []
        for item in (cbr, nbrb, brent, gold, cpi):
            if isinstance(item, MacroIndicator):
                indicators.append(item)

        relevant = self._filter_for_pair(pair, indicators)
        return MacroPanel(pair=pair, indicators=relevant)

    def _filter_for_pair(self, pair: CurrencyPair, items: List[MacroIndicator]) -> List[MacroIndicator]:
        ids_by_pair = {
            "USD_BYN": {"nbrb_rate", "brent", "gold", "cbr_rate", "cpi_ru"},
            "EUR_BYN": {"nbrb_rate", "brent", "gold", "cpi_ru"},
            "EUR_USD": {"brent", "gold", "cbr_rate", "cpi_ru"},
        }
        allowed = ids_by_pair.get(pair, set())
        return [i for i in items if i.id in allowed]

    async def _fetch_cbr_key_rate(self) -> Optional[MacroIndicator]:
        url = "https://www.cbr.ru/scripts/XML_KeyRate.asp"
        async with httpx.AsyncClient(timeout=12) as client:
            r = await client.get(url, params={"date_req": date.today().strftime("%d/%m/%Y")})
            r.raise_for_status()
            root = ET.fromstring(r.content)
            records = root.findall("record")
            if not records:
                return None
            last = records[-1]
            value = float(last.find("Rate").text.replace(",", "."))
            prev_val = value
            if len(records) > 1:
                prev_val = float(records[-2].find("Rate").text.replace(",", "."))
            change = round((value - prev_val) / prev_val * 100, 2) if prev_val else None
            return MacroIndicator(
                id="cbr_rate",
                name="Ключевая ставка ЦБ РФ",
                value=value,
                unit="% годовых",
                change_pct=change,
                impact=IMPACT["cbr_rate"],
                source="cbr.ru",
            )

    async def _fetch_nbrb_refinance(self) -> Optional[MacroIndicator]:
        url = "https://api.nbrb.by/refinancingrate"
        async with httpx.AsyncClient(timeout=12) as client:
            r = await client.get(url)
            r.raise_for_status()
            data = r.json()
            if not data:
                return None
            last = data[-1]
            value = float(last["Value"])
            change = None
            if len(data) > 1:
                prev = float(data[-2]["Value"])
                if prev:
                    change = round((value - prev) / prev * 100, 2)
            return MacroIndicator(
                id="nbrb_rate",
                name="Ставка рефинансирования НБРБ",
                value=value,
                unit="% годовых",
                change_pct=change,
                impact=IMPACT["nbrb_rate"],
                source="nbrb.by",
            )

    async def _fetch_cbr_inflation(self) -> MacroIndicator:
        """Инфляция РФ: публичный ориентир (для курсовой; уточняется по отчётам ЦБ)."""
        return MacroIndicator(
            id="cpi_ru",
            name="Инфляция (РФ, ориентир)",
            value=7.0,
            unit="% г/г",
            change_pct=None,
            impact=IMPACT["cpi_ru"],
            source="cbr.ru / макроотчёт",
        )

    async def _fetch_yahoo_last(self, symbol: str, name: str) -> Optional[MacroIndicator]:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        params = {"interval": "1d", "range": "5d"}
        async with httpx.AsyncClient(timeout=12) as client:
            r = await client.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"})
            r.raise_for_status()
            result = r.json()["chart"]["result"][0]
            closes = result["indicators"]["quote"][0]["close"]
            closes = [c for c in closes if c is not None]
            if not closes:
                return None
            value = float(closes[-1])
            change = None
            if len(closes) > 1 and closes[-2]:
                change = round((value - closes[-2]) / closes[-2] * 100, 2)
            id_map = {"BZ=F": "brent", "GC=F": "gold"}
            return MacroIndicator(
                id=id_map.get(symbol, symbol),
                name=name,
                value=round(value, 2),
                unit="USD",
                change_pct=change,
                impact=IMPACT[id_map.get(symbol, "brent")],
                source="Yahoo Finance",
            )
