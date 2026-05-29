import React, { useEffect, useState } from "react";
import { currencyApi } from "../api/client";
import type { CurrencyPair, ModelMetrics } from "../types";
import { PAIR_LABELS } from "../types";

interface Props {
  pair: CurrencyPair;
}

const MetricsPanel: React.FC<Props> = ({ pair }) => {
  const [metrics, setMetrics] = useState<Record<string, ModelMetrics> | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        setLoading(true);
        const data = await currencyApi.compareMetrics(pair);
        if (!cancelled) setMetrics(data);
      } catch {
        if (!cancelled) setMetrics(null);
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [pair]);

  const sarimax = metrics?.sarimax;
  const gemini = metrics?.gemini;

  return (
    <div className="glass-card">
      <h3>Analytics & AI — {PAIR_LABELS[pair]}</h3>
      {loading ? (
        <p className="loading">Расчёт MAPE/RMSE…</p>
      ) : (
        <div className="metrics-grid">
          <div className="metric-box">
            <div className="metric-box__value">
              {sarimax && sarimax.mape >= 0 ? `${sarimax.mape.toFixed(2)}%` : "—"}
            </div>
            <div className="metric-box__label">SARIMAX MAPE</div>
            {sarimax && sarimax.rmse >= 0 && (
              <div className="metric-box__label">RMSE: {sarimax.rmse.toFixed(4)}</div>
            )}
          </div>
          <div className="metric-box">
            <div className="metric-box__value">
              {gemini && gemini.mape >= 0 ? `${gemini.mape.toFixed(2)}%` : "—"}
            </div>
            <div className="metric-box__label">Gemini MAPE</div>
            {gemini && gemini.rmse >= 0 && (
              <div className="metric-box__label">RMSE: {gemini.rmse.toFixed(4)}</div>
            )}
          </div>
        </div>
      )}
      <p style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginTop: "0.75rem" }}>
        Holdout 30 дней: модель обучается на прошлом, прогноз сравнивается с фактом.
      </p>
    </div>
  );
};

export default MetricsPanel;
