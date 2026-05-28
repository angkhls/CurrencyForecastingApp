import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { currencyApi } from "../api/client";
import type { AllLatestRates, CurrencyCode } from "../types";
import CurrencyCard from "../components/CurrencyCard";

const CURRENCIES: CurrencyCode[] = ["USD", "EUR", "RUB"];

const Dashboard: React.FC = () => {
  const [rates, setRates] = useState<AllLatestRates | null>(null);
  const [loadingRates, setLoadingRates] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchRates = async () => {
      try {
        setLoadingRates(true);
        const data = await currencyApi.getAllLatest();
        setRates(data);
      } catch (e: any) {
        setError(e.message);
      } finally {
        setLoadingRates(false);
      }
    };
    fetchRates();
  }, []);

  return (
    <div className="page">
      <h1 className="page__title">Курсы валют НБ РБ</h1>

      {error && (
        <div className="alert alert--error">Ошибка загрузки: {error}</div>
      )}

      <section className="section">
        <h2 className="section__title">Актуальные курсы</h2>
        <div className="cards">
          {CURRENCIES.map((currency) => (
            <CurrencyCard
              key={currency}
              rate={rates?.[currency] ?? null}
              loading={loadingRates}
            />
          ))}
        </div>
      </section>

      <section className="section">
        <h2 className="section__title">Прогноз и история</h2>
        <div className="cards">
          {CURRENCIES.map((currency) => (
            <Link
              key={currency}
              to={`/forecast/${currency}`}
              className="card card--link"
            >
              <span className="card__currency">{currency} / BYN</span>
              <span className="card__action">Смотреть прогноз →</span>
            </Link>
          ))}
        </div>
      </section>
    </div>
  );
};

export default Dashboard;
