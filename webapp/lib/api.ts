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

export type PerYear = { period: string; return: number | null; sharpe: number | null; bars: number };

export type Diagnostics = {
  n_trials: number;
  deflated_sharpe: number | null;
  trades_per_fold: number | null;
  per_year: PerYear[];
  best_year: string | null;
  best_year_share: number | null;
  regime_split: Record<"up" | "down" | "chop", { return: number; bars: number }> | null;
  red_flags: string[];
};

export type WalkForward = {
  regime: string;
  oos_metrics: Metrics;
  params_per_fold: Record<string, number>[];
  oos_equity: { dates: string[]; net: (number | null)[] } | null;
  diagnostics: Diagnostics | null;
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

// ---- Engine Room types (live /engine page; all computed in Python) ----

export type UniverseTicker = {
  ticker: string;
  sector: string;
  source: "realdata" | "cache" | "alpaca" | "yfinance-fallback" | "none";
  rows: number | null;
  start: string | null;
  end: string | null;
  ok: boolean;
  error: string | null;
};

export type UniverseResponse = {
  tickers: UniverseTicker[];
  summary: {
    n_ok: number;
    n_failed: number;
    cache_age_seconds: number;
    ttl_seconds: number;
    source: string;
    alpaca_configured: boolean;
  };
};

export type ScanRow = {
  ticker: string;
  strategy: string;
  verdict: string;
  metrics: Metrics & { n_trials: number };
  bh_return: number | null;
  rand_return: number | null;
  spy_return: number | null;
  beats_bh: boolean;
  beats_rand: boolean;
  beats_spy: boolean;
  survives_gate2: boolean;
  significant: boolean;
  clean: boolean;
  dsr: number | null;
  red_flags: string[];
  trades_per_fold: number;
  thin: boolean;
};

export type ScanResponse = {
  summary: {
    n_backtests: number;
    n_tickers: number;
    strategies: string[];
    n_edge: number;
    n_suspect: number;
    n_dead: number;
    elapsed_seconds: number;
    n_folds: number;
    min_trades_per_fold: number;
    cost_regime: string;
    has_spy_benchmark: boolean;
  };
  rows: ScanRow[];
};

export type PerYearEntry = { year: number; momentum: number; ew_universe: number | null };

export type SweepEntry = {
  lookback: string;
  top_n: number;
  total_return: number;
  cagr: number;
  sharpe: number;
  max_dd: number;
  beats_ew: boolean;
  canonical: boolean;
};

export type RegimeSplit = Record<"up" | "down" | "chop", { return: number; bars: number }>;

export type MomentumResponse = {
  spec: string;
  window: [string, string];
  bars: number;
  n_names: number;
  portfolios: {
    momentum: Metrics;
    ew_universe: Metrics;
    random: Metrics;
    spy: Metrics | null;
  };
  per_year: PerYearEntry[];
  probabilistic_sharpe: number | null;
  psr_months: number;
  regime_split: RegimeSplit | null;
  red_flags: string[];
  sweep: SweepEntry[];
  sweep_beats_ew: string;
  verdict: { beats_ew: boolean; beats_random: boolean; beats_spy: boolean; survives: boolean };
  caveats: string[];
  elapsed_seconds: number;
};

export type AlpacaPosition = {
  symbol: string;
  qty: number;
  avg_entry_price: number;
  market_value: number;
  unrealized_pl: number;
};

export type AlpacaStatus = {
  configured: boolean;
  reason?: string;
  ok?: boolean;
  error?: string;
  account?: {
    account_number: string;
    status: string;
    equity: number;
    cash: number;
    buying_power: number;
  };
  positions?: AlpacaPosition[];
};

export function fetchTickers() {
  return getJSON<TickersResponse>("/api/tickers");
}

export function fetchUniverse(refresh = false) {
  return getJSON<UniverseResponse>(`/api/universe?refresh=${refresh}`);
}

export function fetchScan(refresh = false) {
  return getJSON<ScanResponse>(`/api/engine/scan?refresh=${refresh}`);
}

export function fetchMomentum(refresh = false) {
  return getJSON<MomentumResponse>(`/api/engine/momentum?refresh=${refresh}`);
}

export function fetchAlpacaStatus() {
  return getJSON<AlpacaStatus>("/api/alpaca/status");
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
export const usd = (v: number | null | undefined) =>
  v === null || v === undefined || Number.isNaN(v)
    ? "—"
    : v.toLocaleString("en-US", { style: "currency", currency: "USD" });
