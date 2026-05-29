import React from "react";
import { BrowserRouter, Navigate, Route, Routes, useParams } from "react-router-dom";
import Layout from "./components/Layout";
import Dashboard from "./pages/Dashboard";
import ForecastPage from "./pages/ForecastPage";
import MacroInfoPage from "./pages/MacroInfoPage";
import MarketPage from "./pages/MarketPage";
import ToolsPage from "./pages/ToolsPage";

const App: React.FC = () => (
  <BrowserRouter>
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/market" element={<MarketPage />} />
        <Route path="/forecast" element={<ForecastPage />} />
        <Route path="/tools" element={<ToolsPage />} />
        <Route path="/macro" element={<MacroInfoPage />} />
      </Route>
      <Route path="/live" element={<Navigate to="/market" replace />} />
      <Route path="/converter" element={<Navigate to="/tools" replace />} />
      <Route path="/history" element={<Navigate to="/tools" replace />} />
      <Route path="/forecast/:pair" element={<ForecastRedirect />} />
    </Routes>
  </BrowserRouter>
);

const ForecastRedirect: React.FC = () => {
  const { pair } = useParams<{ pair: string }>();
  return <Navigate to={`/forecast?pair=${pair ?? "USD_BYN"}`} replace />;
};

export default App;
