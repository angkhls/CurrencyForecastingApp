export type CurrencyCode = "USD" | "EUR" | "RUB";

export interface CurrencyRate {
  currency: CurrencyCode;
  date: string;
  rate: number;
}

export interface ForecastPoint {
  date: string;
  predicted_value: number;
}

export interface ForecastResult {
  currency: CurrencyCode;
  forecast: ForecastPoint[];
}

export type AllLatestRates = Record<CurrencyCode, CurrencyRate | null>;
