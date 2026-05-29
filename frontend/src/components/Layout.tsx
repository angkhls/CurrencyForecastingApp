import React from "react";
import { Outlet, useLocation } from "react-router-dom";
import Sidebar from "./Sidebar";

const TITLES: Record<string, { title: string; subtitle: string }> = {
  "/": { title: "Главная", subtitle: "График, прогноз и макро-факторы" },
  "/market": { title: "Рынок", subtitle: "Актуальные курсы НБРБ" },
  "/forecast": { title: "Прогноз", subtitle: "SARIMAX и Gemini — сравнение методов" },
  "/tools": { title: "Инструменты", subtitle: "Конвертер и исторические курсы" },
  "/macro": { title: "Макроэкономика", subtitle: "Как факторы влияют на валюту" },
};

const Layout: React.FC = () => {
  const { pathname } = useLocation();
  const meta = TITLES[pathname] ?? TITLES["/"];

  return (
    <div className="app-shell">
      <Sidebar />
      <div className="main-area">
        <header className="topbar">
          <div>
            <h1>{meta.title}</h1>
            <p className="topbar__greeting">Welcome back, Anhelina! {meta.subtitle}</p>
          </div>
          <div className="topbar__user">
            <span>Anhelina</span>
            <div className="avatar">A</div>
          </div>
        </header>
        <Outlet />
      </div>
    </div>
  );
};

export default Layout;
