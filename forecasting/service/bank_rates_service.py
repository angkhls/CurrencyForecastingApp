from domain.models import BankCurrencyQuotes, BankRatesTable, BankRow, CurrencyCode
from infrastructure.belarusbank_client import BelarusbankClient
from infrastructure.nbrb_client import NbrbApiClient
class BankRatesService:
    def __init__(self, belarusbank: BelarusbankClient, nbrb: NbrbApiClient):
        self._bb = belarusbank
        self._nbrb = nbrb

    async def get_minsk_table(self) -> BankRatesTable:
        rows: list[BankRow] = []
        city = "Минск"

        try:
            bb_data = await self._bb.fetch_city(city)
            bb_row = self._bb.aggregate_best(bb_data, "Беларусбанк", "belarusbank")
            if bb_row:
                rows.append(bb_row)
        except Exception:
            pass

        try:
            nbrb_row = await self._nbrb_official_row()
            if nbrb_row:
                rows.append(nbrb_row)
        except Exception:
            pass

        return BankRatesTable(city=city, rows=rows, source_note=(
            "Лучшие курсы по отделениям Беларусбанка (API belarusbank.by) и официальный курс НБРБ. "
            "Полный список банков как на myfin.by требует подключения API каждого банка отдельно."
        ))

    async def _nbrb_official_row(self) -> BankRow:
        from datetime import date

        today = date.today()
        usd = await self._nbrb.get_rate("USD", today)
        eur = await self._nbrb.get_rate("EUR", today)
        rub = await self._nbrb.get_rate("RUB", today)
        r100 = rub.rate * 100
        return BankRow(
            bank_id="nbrb",
            bank_name="НБРБ (официальный)",
            usd=BankCurrencyQuotes(sell=usd.rate, buy=usd.rate),
            eur=BankCurrencyQuotes(sell=eur.rate, buy=eur.rate),
            rub100=BankCurrencyQuotes(sell=r100, buy=r100),
        )
