import axios from "axios";
import type { CurrencyCode, CurrencyRate, ForecastResult, AllLatestRates } from "../types";

const http = axios.create({
  baseURL: "/api/v1",
  timeout: 30000,
});

http.interceptors.response.use(
  (response) => response,
  (error) => {
    const message =
      error.response?.data?.detail ?? error.message ?? "Неизвестная ошибка";
    return Promise.reject(new Error(message));
  }
);

export const currencyApi = {
  getAllLatest: async (): Promise<AllLatestRates> => {
    const { data } = await http.get("/rates/all/latest");
    return data;
  },

  getHistory: async (
    currency: CurrencyCode,
    days: number = 30
  ): Promise<CurrencyRate[]> => {
    const { data } = await http.get(`/rates/${currency}/history`, {
      params: { days },
    });
    return data;
  },

  getForecast: async (
    currency: CurrencyCode,
    days: number = 7
  ): Promise<ForecastResult> => {
    const { data } = await http.get(`/rates/${currency}/forecast`, {
      params: { days },
    });
    return data;
  },

  syncRates: async (currency: CurrencyCode): Promise<{ synced: number }> => {
    const { data } = await http.post(`/rates/${currency}/sync`);
    return data;
  },
};
