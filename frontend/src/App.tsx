import React from "react";
import { BrowserRouter, Routes, Route, NavLink } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import ForecastPage from "./pages/ForecastPage";

const App: React.FC = () => {
  return (
    <BrowserRouter>
      <div className="app">
        <header className="navbar">
          <div className="navbar__brand">💱 CurrencyApp</div>
          <nav className="navbar__nav">
            <NavLink
              to="/"
              end
              className={({ isActive }) =>
                isActive ? "nav-link nav-link--active" : "nav-link"
              }
            >
              Дашборд
            </NavLink>
            <NavLink
              to="/forecast/USD"
              className={({ isActive }) =>
                isActive ? "nav-link nav-link--active" : "nav-link"
              }
            >
              USD
            </NavLink>
            <NavLink
              to="/forecast/EUR"
              className={({ isActive }) =>
                isActive ? "nav-link nav-link--active" : "nav-link"
              }
            >
              EUR
            </NavLink>
            <NavLink
              to="/forecast/RUB"
              className={({ isActive }) =>
                isActive ? "nav-link nav-link--active" : "nav-link"
              }
            >
              RUB
            </NavLink>
          </nav>
        </header>
        <main className="main">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/forecast/:currency" element={<ForecastPage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
};

export default App;
