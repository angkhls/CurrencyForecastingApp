from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from domain.models import CurrencyCode, ForecastResult, CurrencyRate
from service.rate_service import RateService

# ─────────────────────────────────────────────
# СЛОЙ PRESENTATION (Представление)
#
# Роутер знает только об HTTP:
# - принять запрос
# - вызвать сервис
# - вернуть ответ или ошибку
#
# Никакой бизнес-логики здесь нет.
# Всё что сложнее "получи и отдай" — в сервисе.
# ─────────────────────────────────────────────

router = APIRouter(prefix="/api/v1", tags=["currency"])


# ── Dependency Injection через FastAPI ────────
# FastAPI сам вызывает get_rate_service() и передаёт
# результат в параметр service каждого эндпоинта.
# Реальный экземпляр подключается в main.py
# через app.dependency_overrides.

def get_rate_service() -> RateService:
    """
    Dependency: возвращает экземпляр RateService.
    Настраивается в main.py через dependency_overrides.
    """
    raise NotImplementedError("Dependency not configured")


# ── Эндпоинты ─────────────────────────────────

@router.get(
    "/rates/{currency}/latest",
    response_model=CurrencyRate,
    summary="Получить актуальный курс валюты"
)
async def get_latest_rate(
    currency: CurrencyCode,
    service: RateService = Depends(get_rate_service)
):
    """
    Возвращает самый свежий курс указанной валюты.
    Если данные устарели — автоматически обновляет их с NBRB.

    Пример: GET /api/v1/rates/USD/latest
    """
    try:
        return await service.get_latest_rate(currency)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get(
    "/rates/{currency}/history",
    response_model=List[CurrencyRate],
    summary="Получить историю курсов"
)
async def get_history(
    currency: CurrencyCode,
    days: int = Query(
        default=30,
        ge=1,
        le=365,
        description="Количество дней истории (1-365)"
    ),
    service: RateService = Depends(get_rate_service)  # ← был баг: Depends не был указан
):
    """
    Возвращает историю курсов за последние N дней.
    Данные отсортированы по дате по возрастанию.

    Пример: GET /api/v1/rates/USD/history?days=90
    """
    try:
        return await service.get_history(currency, days)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/rates/{currency}/forecast",
    response_model=ForecastResult,
    summary="Получить прогноз курса"
)
async def get_forecast(
    currency: CurrencyCode,
    days: int = Query(
        default=7,
        ge=1,
        le=30,
        description="Горизонт прогноза в днях (1-30)"
    ),
    service: RateService = Depends(get_rate_service)
):
    """
    Строит прогноз курса валюты на N дней вперёд с помощью SARIMAX.

    Пример: GET /api/v1/rates/EUR/forecast?days=14
    """
    try:
        return await service.get_forecast(currency, days)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/rates/{currency}/sync",
    summary="Принудительно обновить курсы с NBRB"
)
async def sync_rates(
    currency: CurrencyCode,
    service: RateService = Depends(get_rate_service)
):
    """
    Загружает свежие курсы с api.nbrb.by и сохраняет в БД.
    Возвращает количество загруженных записей.

    Пример: POST /api/v1/rates/USD/sync
    """
    try:
        count = await service.sync_rates(currency)
        return {"synced": count, "currency": currency}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Ошибка NBRB API: {str(e)}")


@router.get(
    "/rates/all/latest",
    summary="Получить актуальные курсы всех валют"
)
async def get_all_latest(
    service: RateService = Depends(get_rate_service)
):
    """
    Возвращает актуальные курсы USD, EUR и RUB одним запросом.
    Удобно для дашборда — один запрос вместо трёх.

    Пример: GET /api/v1/rates/all/latest
    """
    results = {}
    for currency in ["USD", "EUR", "RUB"]:
        try:
            rate = await service.get_latest_rate(currency)
            results[currency] = rate
        except ValueError:
            results[currency] = None
    return results