import React, { useMemo } from "react";
import {
  Area,
  CartesianGrid,
  ComposedChart,
  Line,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { ChartData, ForecastResult } from "../types";
import { PAIR_LABELS } from "../types";

interface Props {
  chart: ChartData | null;
  forecast: ForecastResult | null;
  loading?: boolean;
}

const MainChart: React.FC<Props> = ({ chart, forecast, loading }) => {
  const data = useMemo(() => {
    if (!chart) return [];
    const hist = chart.points.map((p) => ({
      date: new Date(p.date).toLocaleDateString("ru-RU", { day: "2-digit", month: "short" }),
      rate: p.rate,
      sma: p.sma_20 ?? undefined,
      ema: p.ema_20 ?? undefined,
      forecast: undefined as number | undefined,
      lower: undefined as number | undefined,
      upper: undefined as number | undefined,
    }));
    if (!forecast?.forecast.length) return hist;

    const fc = forecast.forecast.map((p) => ({
      date: new Date(p.date).toLocaleDateString("ru-RU", { day: "2-digit", month: "short" }),
      rate: undefined as number | undefined,
      sma: undefined,
      ema: undefined,
      forecast: p.predicted_value,
      lower: p.lower ?? p.predicted_value * 0.98,
      upper: p.upper ?? p.predicted_value * 1.02,
    }));
    return [...hist, ...fc];
  }, [chart, forecast]);

  if (loading) return <div className="loading">Загрузка графика…</div>;
  if (!chart) return null;

  return (
    <div className="chart-card glass-card">
      <div className="chart-header">
        <div className="chart-header__pair">{PAIR_LABELS[chart.pair]}</div>
      </div>
      <ResponsiveContainer width="100%" height={360}>
        <ComposedChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.08)" />
          <XAxis dataKey="date" tick={{ fill: "#9aa8bc", fontSize: 11 }} interval="preserveStartEnd" />
          <YAxis tick={{ fill: "#9aa8bc", fontSize: 11 }} domain={["auto", "auto"]} width={55} />
          <Tooltip
            contentStyle={{
              background: "rgba(20,28,40,0.95)",
              border: "1px solid rgba(255,255,255,0.15)",
              borderRadius: 8,
            }}
          />
          <ReferenceLine y={chart.levels.support} stroke="#4ade80" strokeDasharray="4 4" label="Support" />
          <ReferenceLine y={chart.levels.resistance} stroke="#f87171" strokeDasharray="4 4" label="Resistance" />
          <Line type="monotone" dataKey="rate" stroke="#60a5fa" strokeWidth={2} dot={false} connectNulls={false} />
          <Line type="monotone" dataKey="sma" stroke="#a78bfa" strokeWidth={1.5} dot={false} connectNulls={false} />
          <Line type="monotone" dataKey="ema" stroke="#3dd6c3" strokeWidth={1.5} dot={false} connectNulls={false} />
          <Line type="monotone" dataKey="forecast" stroke="#fbbf24" strokeWidth={2} strokeDasharray="6 3" dot connectNulls={false} />
          <Area type="monotone" dataKey="upper" stackId="band" stroke="none" fill="rgba(96,165,250,0.08)" connectNulls={false} />
          <Area type="monotone" dataKey="lower" stackId="band" stroke="none" fill="rgba(96,165,250,0.08)" connectNulls={false} />
        </ComposedChart>
      </ResponsiveContainer>
      <div className="legend">
        <span className="rate">Курс</span>
        <span className="sma">SMA(20)</span>
        <span className="ema">EMA(20)</span>
        <span className="forecast">Прогноз</span>
      </div>
    </div>
  );
};

export default MainChart;
