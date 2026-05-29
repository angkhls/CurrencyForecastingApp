from datetime import date
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from domain.models import (
    ChartData,
    ConvertResult,
    CurrencyCode,
    CurrencyPair,
    CurrencyRate,
    DashboardResponse,
    ForecastMethod,
    ForecastResult,
    MacroPanel,
    ModelMetrics,
    PeriodPreset,
)
from service.rate_service import RateService

router = APIRouter(prefix="/api/v1", tags=["currency"])


def get_rate_service() -> RateService:
    raise NotImplementedError("Dependency not configured")


@router.get("/dashboard", response_model=DashboardResponse)
async def dashboard(service: RateService = Depends(get_rate_service)):
    return await service.get_dashboard()


@router.get("/rates/{currency}/latest", response_model=CurrencyRate)
async def get_latest_rate(
    currency: CurrencyCode, service: RateService = Depends(get_rate_service)
):
    try:
        return await service.get_latest_rate(currency)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/rates/{currency}/history", response_model=List[CurrencyRate])
async def get_history(
    currency: CurrencyCode,
    days: int = Query(default=30, ge=1, le=3650),
    service: RateService = Depends(get_rate_service),
):
    try:
        return await service.get_history(currency, days)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/rates/{currency}/on/{target_date}", response_model=CurrencyRate)
async def get_rate_on_date(
    currency: CurrencyCode,
    target_date: date,
    service: RateService = Depends(get_rate_service),
):
    try:
        return await service.get_rate_on_date(currency, target_date)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/pairs/{pair}/macro", response_model=MacroPanel)
async def get_macro(
    pair: CurrencyPair,
    service: RateService = Depends(get_rate_service),
):
    try:
        return await service.get_macro(pair)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/pairs/{pair}/chart", response_model=ChartData)
async def get_chart(
    pair: CurrencyPair,
    period: PeriodPreset = Query(default="month"),
    service: RateService = Depends(get_rate_service),
):
    try:
        return await service.get_chart(pair, period)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/pairs/{pair}/forecast", response_model=ForecastResult)
async def get_forecast(
    pair: CurrencyPair,
    days: int = Query(default=7, ge=1, le=30),
    method: ForecastMethod = Query(default="sarimax"),
    service: RateService = Depends(get_rate_service),
):
    try:
        return await service.get_forecast(pair, days, method)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/pairs/{pair}/metrics", response_model=ModelMetrics)
async def get_metrics(
    pair: CurrencyPair,
    method: ForecastMethod = Query(default="sarimax"),
    holdout_days: int = Query(default=30, ge=7, le=90),
    service: RateService = Depends(get_rate_service),
):
    try:
        return await service.get_metrics(pair, method, holdout_days)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/pairs/{pair}/metrics/compare")
async def compare_metrics(
    pair: CurrencyPair, service: RateService = Depends(get_rate_service)
):
    try:
        return await service.compare_methods(pair)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/convert", response_model=ConvertResult)
async def convert(
    amount: float = Query(gt=0),
    from_currency: CurrencyCode = Query(alias="from"),
    to_currency: CurrencyCode = Query(alias="to"),
    service: RateService = Depends(get_rate_service),
):
    try:
        return await service.convert(amount, from_currency, to_currency)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/rates/{currency}/sync")
async def sync_rates(
    currency: CurrencyCode, service: RateService = Depends(get_rate_service)
):
    try:
        count = await service.sync_rates(currency)
        return {"synced": count, "currency": currency}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Ошибка NBRB API: {e}")


@router.get("/rates/all/latest")
async def get_all_latest(service: RateService = Depends(get_rate_service)):
    results = {}
    for currency in ["USD", "EUR", "RUB", "CNY"]:
        try:
            results[currency] = await service.get_latest_rate(currency)
        except ValueError:
            results[currency] = None
    return results
