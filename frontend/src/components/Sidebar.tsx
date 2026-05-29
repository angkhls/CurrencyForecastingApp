import React from "react";
import { NavLink } from "react-router-dom";
import type { CurrencyPair } from "../types";
import { PAIR_LABELS } from "../types";

const PAIRS: CurrencyPair[] = ["USD_BYN", "EUR_BYN", "EUR_USD"];

const Sidebar: React.FC = () => (
  <aside className="sidebar">
    <div className="sidebar__brand">
      <div className="sidebar__logo">💱</div>
      <span>CurrencyForecastingApp</span>
    </div>
    <nav className="sidebar__nav">
      <NavLink to="/" end className={({ isActive }) => (isActive ? "nav-link nav-link--active" : "nav-link")}>
        🏠 Home
      </NavLink>
      <NavLink to="/live" className={({ isActive }) => (isActive ? "nav-link nav-link--active" : "nav-link")}>
        📈 Live Market
      </NavLink>
      <div className="nav-group__title">AI Forecasts</div>
      {PAIRS.map((pair) => (
        <NavLink
          key={pair}
          to={`/forecast/${pair}`}
          className={({ isActive }) => (isActive ? "nav-link nav-link--active" : "nav-link")}
        >
          🔮 {PAIR_LABELS[pair]}
        </NavLink>
      ))}
      <NavLink to="/converter" className={({ isActive }) => (isActive ? "nav-link nav-link--active" : "nav-link")}>
        🔄 Конвертер
      </NavLink>
      <NavLink to="/history" className={({ isActive }) => (isActive ? "nav-link nav-link--active" : "nav-link")}>
        📅 История
      </NavLink>
    </nav>
  </aside>
);

export default Sidebar;
