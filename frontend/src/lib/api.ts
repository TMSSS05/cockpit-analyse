export interface Asset {
  symbol: string;
  name: string;
  timeframes: string[];
}

export interface Candle {
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface CandlesResponse {
  symbol: string;
  timeframe: string;
  count: number;
  candles: Candle[];
}

export interface Indicators {
  ema_20: number;
  ema_50: number;
  ema_200: number;
  rsi: number;
  atr: number;
  adx: number;
  bb_upper: number;
  bb_middle: number;
  bb_lower: number;
  macd_line: number;
  macd_signal: number;
  macd_hist: number;
}

export interface Structure {
  trend: string;
  momentum: string;
  volatility: string;
  consolidation: boolean;
  breakout: boolean;
  sweep: boolean;
}

export interface Score {
  value: number;
  label: string;
  action_bias: string;
}

export interface Scenario {
  title: string;
  direction: string;
  probability: number;
  description: string;
  target?: number;
  invalidation?: number;
}

export interface AnalysisResponse {
  symbol: string;
  timeframe: string;
  price: number;
  timestamp: string;
  indicators: Indicators;
  structure: Structure;
  score: Score;
  scenarios: Scenario[];
}

export interface Level {
  type: string;
  price: number;
  importance: string;
}

export interface LevelsResponse {
  symbol: string;
  timeframe: string;
  current_price: number;
  levels: Level[];
  closest_level: Level | null;
}

export interface BriefAsset {
  symbol: string;
  name: string;
  price: number;
  score: { value: number; label: string; action_bias: string };
  scenario_count: number;
}

export interface BriefResponse {
  timeframe: string;
  asset_count: number;
  assets: BriefAsset[];
}

export interface DrawingPoint {
  timestamp?: number | null;
  price?: number | null;
  value?: number | null;
}

export interface DrawingCreate {
  symbol: string;
  timeframe: string;
  overlay_name: string;
  id?: string | null;
  points?: DrawingPoint[];
  styles?: Record<string, unknown>;
}

export interface DrawingUpdate {
  points?: DrawingPoint[];
  styles?: Record<string, unknown>;
}

export interface DrawingOut {
  id: string;
  symbol: string;
  timeframe: string;
  overlay_name: string;
  points: DrawingPoint[];
  styles: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface DrawingsResponse {
  drawings: DrawingOut[];
}

async function fetchJSON<T>(path: string): Promise<T> {
  const res = await fetch(path);
  if (!res.ok) {
    throw new Error(`API ${res.status}: ${res.statusText}`);
  }
  return res.json();
}

async function postJSON<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    throw new Error(`API POST ${res.status}: ${res.statusText}`);
  }
  return res.json();
}

async function putJSON<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(path, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    throw new Error(`API PUT ${res.status}: ${res.statusText}`);
  }
  return res.json();
}

async function delJSON<T>(path: string): Promise<T> {
  const res = await fetch(path, { method: "DELETE" });
  if (!res.ok) {
    throw new Error(`API DELETE ${res.status}: ${res.statusText}`);
  }
  return res.json();
}

export function getAssets(): Promise<{ assets: Asset[] }> {
  return fetchJSON("/api/assets");
}

export function getCandles(
  symbol: string,
  timeframe = "1h",
  limit = 200
): Promise<CandlesResponse> {
  return fetchJSON(
    `/api/candles/${symbol}?timeframe=${timeframe}&limit=${limit}`
  );
}

export function getAnalysis(
  symbol: string,
  timeframe = "1h"
): Promise<AnalysisResponse> {
  return fetchJSON(`/api/analysis/${symbol}?timeframe=${timeframe}`);
}

export function getLevels(
  symbol: string,
  timeframe = "4h"
): Promise<LevelsResponse> {
  return fetchJSON(`/api/levels/${symbol}?timeframe=${timeframe}`);
}

export function getBrief(
  timeframe = "4h"
): Promise<BriefResponse> {
  return fetchJSON(`/api/brief?timeframe=${timeframe}`);
}

export function getDrawings(symbol: string, timeframe = "1h"): Promise<DrawingsResponse> {
  return fetchJSON(`/api/drawings/${symbol}?timeframe=${timeframe}`);
}

export function createDrawing(body: DrawingCreate): Promise<DrawingOut> {
  return postJSON("/api/drawings", body);
}

export function updateDrawing(id: string, body: DrawingUpdate): Promise<DrawingOut> {
  return putJSON(`/api/drawings/${id}`, body);
}

export function deleteDrawing(id: string): Promise<{ deleted: string }> {
  return delJSON(`/api/drawings/${id}`);
}
