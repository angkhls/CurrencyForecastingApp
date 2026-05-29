import React from "react";
import { NavLink } from "react-router-dom";

const Sidebar: React.FC = () => (
  <aside className="sidebar">
    <div className="sidebar__brand">
      <div className="sidebar__logo">💱</div>
      <span>CurrencyForecastingApp</span>
    </div>
    <nav className="sidebar__nav">
      <NavLink to="/" end className={({ isActive }) => (isActive ? "nav-link nav-link--active" : "nav-link")}>
        🏠 Главная
      </NavLink>
      <NavLink to="/market" className={({ isActive }) => (isActive ? "nav-link nav-link--active" : "nav-link")}>
        📊 Рынок
      </NavLink>
      <NavLink to="/forecast" className={({ isActive }) => (isActive ? "nav-link nav-link--active" : "nav-link")}>
        🔮 Прогноз
      </NavLink>
      <NavLink to="/tools" className={({ isActive }) => (isActive ? "nav-link nav-link--active" : "nav-link")}>
        🛠 Инструменты
      </NavLink>
      <NavLink to="/macro" className={({ isActive }) => (isActive ? "nav-link nav-link--active" : "nav-link")}>
        📚 Макро
      </NavLink>
    </nav>
  </aside>
);

export default Sidebar;
