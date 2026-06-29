# Web App — SPEC (the visualizer)

Home: [[PROJECT_PLAN]] · Owner: Tenzing · Status: design

## What it is, in one sentence
A web app where you pick a ticker and date range and see **three things on one chart** — what
the stock actually did, what our model predicted, and the trades our strategy would have
taken — then simulate **"if we paid per trade, what would we actually have?"** net of real
costs, benchmarked against just holding SPY. Plus **live quotes** for display.

## Why we're building it
- It's the portfolio centerpiece all three of us can show.
- It makes the harness's verdicts *visible* to the finance two (no Python required).
- It's where Tenzing's Supabase + Vercel + MCP learning lands.
- Modeling options here is **zero capital risk** — the safe way to "trade" options.

## Core views (build in this order)
1. **Replay (equities first).** Chart of actual price + model signal overlay (long/flat/short
   shading) + markers where trades fire. Toggle strategies.
2. **Pay-per-trade simulator.** Apply `costs.py` (spread+slippage+fee) to every simulated
   trade → show the **net equity curve** vs **buy-and-hold** vs **SPY**. This is the whole
   point: the gap between the pretty signal and the after-cost reality.
3. **Verdict panel.** OOS-net-of-costs number, Sharpe, max drawdown, # trades — pulled
   straight from `metrics.py`. Mirrors [[plan/02-verdict-log]].
4. **Live quotes.** Current price/quote via the Robinhood MCP, **display only** — never
   auto-trading. Clearly labeled "live, not a recommendation."
5. **Options layer (later, labeled APPROXIMATE).** See [[webapp/options-modeling]].

## Architecture (the clean, modern version — and a learning ladder)
The split: **Python produces truth, the web app displays it.** Don't reimplement the
backtest in JavaScript — that's how the numbers drift apart and lie.

```
.py harness  ──exports──▶  results JSON  ──read by──▶  Next.js front end (Vercel)
(costs/backtest/                                   live quotes ◀── Robinhood MCP
 walkforward/metrics)        Supabase (Postgres) ◀── recorded daily option chains (later)
```

- **Phase A (ship fast):** harness writes a `results.json` (price series, signals, equity
  curves, metrics). Static Next.js app on Vercel reads it and charts it. No backend yet.
  Recharts or lightweight-charts for plotting. **This alone is a real portfolio piece.**
- **Phase B (add live + storage):** Supabase Postgres to store runs and (critically) to
  **record live option chains daily** — the only honest path to real options backtests.
  This is the real reason to learn RLS, edge functions, a cron job.
- **Phase C (interactive):** let the user change cost assumptions / parameters in the UI and
  re-request a run (small FastAPI service wrapping the harness, or serverless).

## What "done" looks like for v1
Pick AAPL, see its real path + an SMA strategy's signals, hit simulate, and watch the
after-cost equity curve fall below buy-and-hold — *viscerally seeing why costs kill edges.*
If the app makes that lesson obvious, it's working.

## Non-goals (don't build these)
- No order execution / auto-trading. Display only.
- No JavaScript reimplementation of the backtest math.
- No user accounts for outsiders (see [[plan/05-risk-register]]).
