import React from "react";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import ConverterPage from "./pages/ConverterPage";
import Dashboard from "./pages/Dashboard";
import ForecastPage from "./pages/ForecastPage";
import HistoryPage from "./pages/HistoryPage";

const App: React.FC = () => (
  <BrowserRouter>
    <div className="app-shell">
      <Sidebar />
      <div className="main-area">
        <header className="topbar">
          <div>
            <h1>Dashboard</h1>
            <p className="topbar__greeting">Welcome back, Anhelina! Your Currency Hub.</p>
          </div>
          <div className="topbar__user">
            <span>Anhelina</span>
            <div className="avatar">A</div>
          </div>
        </header>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/live" element={<Dashboard />} />
          <Route path="/forecast/:pair" element={<ForecastPage />} />
          <Route path="/converter" element={<ConverterPage />} />
          <Route path="/history" element={<HistoryPage />} />
        </Routes>
      </div>
    </div>
  </BrowserRouter>
);

export default App;
