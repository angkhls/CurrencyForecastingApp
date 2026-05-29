import React, { useCallback, useEffect, useState } from "react";
import { currencyApi } from "../api/client";
import MainChart from "../components/MainChart";
import MarketPanel from "../components/MarketPanel";
import MetricsPanel from "../components/MetricsPanel";
import type {
  ChartData,
  CurrencyPair,
  DashboardRate,
  ForecastMethod,
  ForecastResult,
  PeriodPreset,
} from "../types";
import { PAIR_LABELS, PERIOD_LABELS } from "../types";

const PERIODS: PeriodPreset[] = ["day", "week", "month", "year", "all"];

const Dashboard: React.FC = () => {
  const [pair, setPair] = useState<CurrencyPair>("USD_BYN");
  const [period, setPeriod] = useState<PeriodPreset>("month");
  const [method, setMethod] = useState<ForecastMethod>("sarimax");
  const [forecastDays, setForecastDays] = useState(7);
  const [rates, setRates] = useState<DashboardRate[]>([]);
  const [chart, setChart] = useState<ChartData | null>(null);
  const [forecast, setForecast] = useState<ForecastResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const [dashboard, chartData, forecastData] = await Promise.all([
        currencyApi.getDashboard(),
        currencyApi.getChart(pair, period),
        currencyApi.getForecast(pair, forecastDays, method),
      ]);
      setRates(dashboard.rates);
      setChart(chartData);
      setForecast(forecastData);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Ошибка загрузки");
    } finally {
      setLoading(false);
    }
  }, [pair, period, method, forecastDays]);

  useEffect(() => {
    load();
  }, [load]);

  return (
    <div className="dashboard-grid">
      <div>
        {error && <div className="alert alert--error">{error}</div>}
        <div className="glass-card" style={{ marginBottom: "1rem" }}>
          <div className="forecast-controls">
            <select className="select" value={pair} onChange={(e) => setPair(e.target.value as CurrencyPair)}>
              {(Object.keys(PAIR_LABELS) as CurrencyPair[]).map((p) => (
                <option key={p} value={p}>
                  {PAIR_LABELS[p]}
                </option>
              ))}
            </select>
            <div className="pill-group">
              {PERIODS.map((p) => (
                <button
                  key={p}
                  type="button"
                  className={period === p ? "pill pill--active" : "pill"}
                  onClick={() => setPeriod(p)}
                >
                  {PERIOD_LABELS[p]}
                </button>
              ))}
            </div>
            <select className="select" value={method} onChange={(e) => setMethod(e.target.value as ForecastMethod)}>
              <option value="sarimax">SARIMAX</option>
              <option value="gemini">Gemini AI</option>
            </select>
            <label style={{ fontSize: "0.85rem", color: "var(--text-muted)" }}>
              Прогноз: {forecastDays} дн.
              <input
                type="range"
                min={1}
                max={30}
                value={forecastDays}
                onChange={(e) => setForecastDays(Number(e.target.value))}
                style={{ display: "block", width: "120px" }}
              />
            </label>
          </div>
          {forecast?.mape != null && (
            <p style={{ fontSize: "0.85rem", color: "var(--text-muted)", margin: "0 0 0.5rem" }}>
              Точность ({method}): MAPE {forecast.mape.toFixed(2)}%, RMSE {forecast.rmse?.toFixed(4) ?? "—"}
            </p>
          )}
        </div>
        <MainChart chart={chart} forecast={forecast} loading={loading} />
      </div>
      <div className="widgets-column">
        <MarketPanel rates={rates} loading={loading} />
        <MetricsPanel pair={pair} />
      </div>
    </div>
  );
};

export default Dashboard;
