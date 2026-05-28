import React, { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { currencyApi } from "../api/client";
import type { CurrencyCode, CurrencyRate, ForecastResult } from "../types";
import HistoryChart from "../components/HistoryChart";
import ForecastChart from "../components/ForecastChart";

const ForecastPage: React.FC = () => {
  const { currency } = useParams<{ currency: string }>();
  const [history, setHistory] = useState<CurrencyRate[]>([]);
  const [forecast, setForecast] = useState<ForecastResult | null>(null);
  const [historyDays, setHistoryDays] = useState(90);
  const [forecastDays, setForecastDays] = useState(7);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!currency) return;
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        const [historyData, forecastData] = await Promise.all([
          currencyApi.getHistory(currency as CurrencyCode, historyDays),
          currencyApi.getForecast(currency as CurrencyCode, forecastDays),
        ]);
        setHistory(historyData);
        setForecast(forecastData);
      } catch (e: any) {
        setError(e.message);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [currency, historyDays, forecastDays]);

  return (
    <div className="page">
      <div className="page__header">
        <Link to="/" className="back-link">← Назад</Link>
        <h1 className="page__title">{currency} / BYN</h1>
      </div>
      {error && <div className="alert alert--error">Ошибка: {error}</div>}
      <div className="controls">
        <div className="control">
          <label className="control__label">История: {historyDays} дней</label>
          <input type="range" min={30} max={365} step={30} value={historyDays}
            onChange={(e) => setHistoryDays(Number(e.target.value))} className="control__slider" />
        </div>
        <div className="control">
          <label className="control__label">Прогноз: {forecastDays} дней</label>
          <input type="range" min={1} max={30} step={1} value={forecastDays}
            onChange={(e) => setForecastDays(Number(e.target.value))} className="control__slider" />
        </div>
      </div>
      {loading ? (
        <div className="loading">Загрузка данных и построение прогноза...</div>
      ) : (
        <>
          <section className="section">
            <ForecastChart history={history} forecast={forecast} currency={currency ?? ""} />
          </section>
          <section className="section">
            <HistoryChart data={history} currency={currency ?? ""} />
          </section>
          {forecast && (
            <section className="section">
              <h3 className="section__title">Прогноз по дням</h3>
              <table className="table">
                <thead><tr><th>Дата</th><th>Прогноз курса</th></tr></thead>
                <tbody>
                  {forecast.forecast.map((point) => (
                    <tr key={point.date}>
                      <td>{new Date(point.date).toLocaleDateString("ru-RU")}</td>
                      <td>{point.predicted_value.toFixed(4)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </section>
          )}
        </>
      )}
    </div>
  );
};

export default ForecastPage;
