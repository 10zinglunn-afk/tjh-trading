// Thin client for the Python harness API. All numbers come from canonical Python;
// this file only fetches and types them — it never computes a backtest.

export const API_URL =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") || "http://127.0.0.1:8000";

export type Metrics = {
  total_return: number | null;
  cagr: number | null;
  sharpe: number | null;
  ann_vol: number | null;
  max_drawdown: number | null;
  num_trades: number | null;
  avg_turnover: number | null;
  win_rate: number | null;
  ev_per_trade_frac: number | null;
  bars: number | null;
};

export type Trade = { date: string; from: number; to: number; price: number };

export type StrategyResult = {
  label: string;
  description: string;
  tunable: boolean;
  positions: (number | null)[];
  trades: Trade[];
  equity_regime: string;
  equity: { gross: (number | null)[]; net: (number | null)[] };
};

export type CostRegime = { label: string; spread_bps: number; slippage_bps: number };

export type WalkForward = {
  regime: string;
  oos_metrics: Metrics;
  params_per_fold: Record<string, number>[];
  oos_equity: { dates: string[]; net: (number | null)[] } | null;
};

export type DataQuality = { level: string; code: string; message: string; rows?: number };

export type Results = {
  schema_version: number;
  generated_at: string;
  meta: {
    name: string;
    source: string;
    bars: number;
    start: string;
    end: string;
    periods_per_year: number;
    display_regime: string;
  };
  data_quality: DataQuality[];
  cost_regimes: Record<string, CostRegime>;
  prices: { dates: string[]; close: (number | null)[] };
  strategies: Record<string, StrategyResult>;
  metrics: Record<string, Record<string, Metrics>>;
  walk_forward: Record<string, WalkForward>;
};

export type TickerInfo = { id: string; label: string; source: string };
export type StrategyInfo = { id: string; label: string; description: string; tunable: boolean };
export type TickersResponse = {
  tickers: TickerInfo[];
  note: string;
  strategies: StrategyInfo[];
};

async function getJSON<T>(path: string): Promise<T> {
  const res = await fetch(`${API_URL}${path}`);
  if (!res.ok) {
    let detail = res.statusText;
    try {
      detail = (await res.json()).detail ?? detail;
    } catch {}
    throw new Error(detail);
  }
  return res.json();
}

export function fetchTickers() {
  return getJSON<TickersResponse>("/api/tickers");
}

export function fetchRun(opts: {
  ticker: string;
  spread_bps: number;
  slippage_bps: number;
}) {
  const q = new URLSearchParams({
    ticker: opts.ticker,
    spread_bps: String(opts.spread_bps),
    slippage_bps: String(opts.slippage_bps),
  });
  return getJSON<Results>(`/api/run?${q.toString()}`);
}

// ---- formatting helpers ----
export const pct = (v: number | null | undefined, dp = 1) =>
  v === null || v === undefined || Number.isNaN(v) ? "—" : `${(v * 100).toFixed(dp)}%`;
export const num = (v: number | null | undefined, dp = 2) =>
  v === null || v === undefined || Number.isNaN(v) ? "—" : v.toFixed(dp);
