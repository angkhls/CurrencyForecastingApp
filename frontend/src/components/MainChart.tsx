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

function parseIso(iso: string): Date {
  return new Date(iso.includes("T") ? iso : `${iso}T12:00:00`);
}

function isWeekendDate(d: Date): boolean {
  const day = d.getDay();
  return day === 0 || day === 6;
}

const MainChart: React.FC<Props> = ({ chart, forecast, loading }) => {
  const { data, yDomain } = useMemo(() => {
    if (!chart) return { data: [], yDomain: [0, 1] as [number, number] };

    const hist = chart.points.map((p) => {
      const dt = parseIso(p.date);
      return {
        date: dt.toLocaleDateString("ru-RU", { day: "2-digit", month: "short" }),
        dateIso: p.date,
        isWeekend: p.is_weekend || isWeekendDate(dt),
        rate: p.rate,
        sma: p.sma_20 ?? undefined,
        ema: p.ema_20 ?? undefined,
        forecast: undefined as number | undefined,
        lower: undefined as number | undefined,
        upper: undefined as number | undefined,
      };
    });

    let rows = hist;
    if (forecast?.forecast.length) {
      const fc = forecast.forecast.map((p) => {
        const dt = parseIso(p.date);
        return {
          date: dt.toLocaleDateString("ru-RU", { day: "2-digit", month: "short" }),
          dateIso: p.date,
          isWeekend: isWeekendDate(dt),
          rate: undefined as number | undefined,
          sma: undefined,
          ema: undefined,
          forecast: p.predicted_value,
          lower: p.lower ?? p.predicted_value * 0.995,
          upper: p.upper ?? p.predicted_value * 1.005,
        };
      });
      rows = [...hist, ...fc];
    }

    const values: number[] = [];
    chart.points.forEach((p) => {
      values.push(p.rate);
      if (p.sma_20 != null) values.push(p.sma_20);
      if (p.ema_20 != null) values.push(p.ema_20);
    });
    values.push(chart.levels.support, chart.levels.resistance);
    forecast?.forecast.forEach((p) => {
      values.push(p.predicted_value);
      if (p.lower != null) values.push(p.lower);
      if (p.upper != null) values.push(p.upper);
    });

    let yMin = chart.y_min;
    let yMax = chart.y_max;
    if (values.length) {
      yMin = Math.min(yMin, ...values);
      yMax = Math.max(yMax, ...values);
    }
    const span = yMax - yMin || yMin * 0.02 || 0.1;
    const pad = Math.max(span * 0.06, 0.015);

    return {
      data: rows,
      yDomain: [yMin - pad, yMax + pad] as [number, number],
    };
  }, [chart, forecast]);

  if (loading) return <div className="loading">Загрузка графика…</div>;
  if (!chart) return null;

  return (
    <div className="chart-card glass-card">
      <div className="chart-header">
        <div className="chart-header__pair">{PAIR_LABELS[chart.pair]}</div>
        <span className="chart-y-hint">
          Ось Y: {yDomain[0].toFixed(4)} — {yDomain[1].toFixed(4)}
        </span>
      </div>
      <ResponsiveContainer width="100%" height={360}>
        <ComposedChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.08)" />
          <XAxis
            dataKey="date"
            tick={{ fill: "#9aa8bc", fontSize: 11 }}
            interval="preserveStartEnd"
            tickFormatter={(label, index) => {
              const row = data[index];
              return row?.isWeekend ? `·${label}` : label;
            }}
          />
          <YAxis
            tick={{ fill: "#9aa8bc", fontSize: 11 }}
            domain={yDomain}
            width={58}
            tickFormatter={(v: number) => v.toFixed(4)}
            allowDataOverflow
          />
          <Tooltip
            contentStyle={{
              background: "rgba(20,28,40,0.95)",
              border: "1px solid rgba(255,255,255,0.15)",
              borderRadius: 8,
            }}
            formatter={(value: number, name: string) => [
              typeof value === "number" ? value.toFixed(4) : value,
              name,
            ]}
          />
          <ReferenceLine
            y={chart.levels.support}
            stroke="#4ade80"
            strokeDasharray="4 4"
            label={{ value: "Support", fill: "#4ade80", fontSize: 10 }}
          />
          <ReferenceLine
            y={chart.levels.resistance}
            stroke="#f87171"
            strokeDasharray="4 4"
            label={{ value: "Resistance", fill: "#f87171", fontSize: 10 }}
          />
          <Line
            type="monotone"
            dataKey="rate"
            name="Курс"
            stroke="#60a5fa"
            strokeWidth={2}
            dot={false}
            connectNulls={false}
          />
          <Line
            type="monotone"
            dataKey="sma"
            name="SMA(20)"
            stroke="#a78bfa"
            strokeWidth={1.5}
            dot={false}
            connectNulls={false}
          />
          <Line
            type="monotone"
            dataKey="ema"
            name="EMA(20)"
            stroke="#3dd6c3"
            strokeWidth={1.5}
            dot={false}
            connectNulls={false}
          />
          <Line
            type="monotone"
            dataKey="forecast"
            name="Прогноз"
            stroke="#fbbf24"
            strokeWidth={2}
            strokeDasharray="6 3"
            dot={false}
            connectNulls
          />
          <Area
            type="monotone"
            dataKey="upper"
            stackId="band"
            stroke="none"
            fill="rgba(96,165,250,0.1)"
            connectNulls={false}
          />
          <Area
            type="monotone"
            dataKey="lower"
            stackId="band"
            stroke="none"
            fill="rgba(96,165,250,0.1)"
            connectNulls={false}
          />
        </ComposedChart>
      </ResponsiveContainer>
      <div className="legend">
        <span className="rate">Курс (рабочие дни)</span>
        <span className="sma">SMA(20)</span>
        <span className="ema">EMA(20)</span>
        <span className="forecast">Прогноз (выходные = последний рабочий)</span>
      </div>
    </div>
  );
};

export default MainChart;
