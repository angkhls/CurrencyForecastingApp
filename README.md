# CurrencyForecastingApp

Веб-приложение для **мониторинга и прогнозирования валютных курсов** (курсовая работа).

**Стек:** Python, FastAPI, React, API [НБРБ](https://www.nbrb.by/apihelp), SARIMAX (statsmodels), Google Gemini.

## Откуда берутся данные

Официальные курсы валют к белорусскому рублю (BYN) загружаются с **API Национального банка Республики Беларусь**:

- `https://api.nbrb.by/exrates/rates/{id}` — курс на дату
- `https://api.nbrb.by/exrates/rates/dynamics/{id}` — история за период

Поддерживаются: **USD, EUR, RUB, CNY** (к BYN).

Пары для графиков и прогноза:

| Пара | Как считается |
|------|----------------|
| **USD/BYN** | курс доллара из НБРБ |
| **EUR/BYN** | курс евро из НБРБ |
| **EUR/USD** | кросс-курс: EUR÷USD по дням |

Данные кэшируются в **SQLite** (по умолчанию) или PostgreSQL.

## Как строится прогноз

### SARIMAX

Статистическая модель временных рядов (Seasonal ARIMA). Обучается на **истории официальных курсов за ~1 год**, затем экстраполирует на 1–30 дней. Параметры: `order=(1,1,1)`, `seasonal_order=(1,1,1,5)` (недельная сезонность по рабочим дням НБРБ).

### Gemini

В промпт передаётся JSON с последними ~90 точками истории; модель возвращает прогноз на N дней. Нужен ключ **GEMINI_API_KEY** ([Google AI Studio](https://aistudio.google.com/apikey)).

### Метрики MAPE / RMSE

Backtest: последние 30 дней откладываются как «будущее», модель обучается на остальном и прогнозирует эти 30 дней; сравнение с фактом даёт MAPE (%) и RMSE.

---

## Установка с нуля (Linux)

### 1. Системные пакеты

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip nodejs npm
```

Проверка: `python3 --version` (≥3.10), `node --version` (≥18).

### 2. Backend

```bash
cd forecasting
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Отредактируйте .env — вставьте GEMINI_API_KEY (для метода Gemini)
```

Запуск API:

```bash
cd forecasting
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Документация: http://localhost:8000/docs

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Откройте: http://localhost:3000

---

## Переменные окружения (`forecasting/.env`)

```env
STORAGE=sqlite
GEMINI_API_KEY=ваш_ключ
```

Для PostgreSQL + Docker:

```bash
cd infra
docker compose up -d
# в .env: STORAGE=postgres, DATABASE_URL=postgresql://currency_user:currency_pass@localhost:5432/currencydb
```

---

## Основные возможности UI

- Интерактивные графики с периодами: день / неделя / месяц / год / всё время
- SMA(20), EMA(20), уровни поддержки и сопротивления
- Дашборд с актуальными курсами и % изменения за неделю
- Конвертер валют по курсам НБРБ
- Исторический курс на выбранную дату
- Прогноз **SARIMAX** или **Gemini** для USD/BYN, EUR/BYN, EUR/USD
- Сравнение MAPE/RMSE между методами

---

## Структура проекта

```
CurrencyForecastingApp/
├── forecasting/          # FastAPI + ML
│   ├── api/routes.py
│   ├── service/          # SARIMAX, Gemini, тех. анализ
│   ├── infrastructure/   # NBRB, SQLite/Postgres
│   └── main.py
├── frontend/             # React + Vite + Recharts
└── infra/docker-compose.yml
```

---

## API (кратко)

| Метод | Путь |
|-------|------|
| GET | `/api/v1/dashboard` |
| GET | `/api/v1/pairs/{pair}/chart?period=month` |
| GET | `/api/v1/pairs/{pair}/forecast?days=7&method=sarimax` |
| GET | `/api/v1/pairs/{pair}/metrics/compare` |
| GET | `/api/v1/convert?amount=100&from=USD&to=EUR` |
| GET | `/api/v1/rates/USD/on/2024-06-01` |

`pair`: `USD_BYN`, `EUR_BYN`, `EUR_USD`
