import React, { useCallback, useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { currencyApi } from "../api/client";
import MainChart from "../components/MainChart";
import MetricsPanel from "../components/MetricsPanel";
import type { ChartData, CurrencyPair, ForecastMethod, ForecastResult, PeriodPreset } from "../types";
import { PAIR_LABELS, PERIOD_LABELS } from "../types";

const PERIODS: PeriodPreset[] = ["week", "month", "year"];

const ForecastPage: React.FC = () => {
  const { pair: pairParam } = useParams<{ pair: string }>();
  const pair = (pairParam ?? "USD_BYN") as CurrencyPair;
  const [period, setPeriod] = useState<PeriodPreset>("month");
  const [method, setMethod] = useState<ForecastMethod>("sarimax");
  const [days, setDays] = useState(7);
  const [chart, setChart] = useState<ChartData | null>(null);
  const [forecast, setForecast] = useState<ForecastResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const [chartData, forecastData] = await Promise.all([
        currencyApi.getChart(pair, period),
        currencyApi.getForecast(pair, days, method),
      ]);
      setChart(chartData);
      setForecast(forecastData);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Ошибка");
    } finally {
      setLoading(false);
    }
  }, [pair, period, method, days]);

  useEffect(() => {
    load();
  }, [load]);

  return (
    <div className="dashboard-grid">
      <div>
        <h2 style={{ marginTop: 0 }}>{PAIR_LABELS[pair]}</h2>
        {error && <div className="alert alert--error">{error}</div>}
        <div className="glass-card" style={{ marginBottom: "1rem" }}>
          <div className="forecast-controls">
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
            <select value={method} className="select" onChange={(e) => setMethod(e.target.value as ForecastMethod)}>
              <option value="sarimax">SARIMAX</option>
              <option value="gemini">Gemini AI</option>
            </select>
            <span>Прогноз: {days} дн.</span>
            <input type="range" min={1} max={30} value={days} onChange={(e) => setDays(Number(e.target.value))} />
          </div>
        </div>
        <MainChart chart={chart} forecast={forecast} loading={loading} />
      </div>
      <div className="widgets-column">
        <MetricsPanel pair={pair} />
      </div>
    </div>
  );
};

export default ForecastPage;
