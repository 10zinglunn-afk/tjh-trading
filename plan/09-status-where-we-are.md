# 09 — STATUS: Where We Are (living tracker)

Home: [[PROJECT_PLAN]] · Charter: [[plan/07-charter-what-we-do]] · Decisions: [[plan/01-decision-log]]

*The single "where are we right now" page. Update this whenever a stage moves. If you (or
Claude) are catching up cold, read this first, then the charter. Last updated: 2026-06-30.*

## The mission, in one line
Find ONE signal that beats buy-and-hold OOS net of realistic costs on real equity data, prove
it honestly, and make the proof visible. We have **zero survivors so far** — that's expected.

## The pipeline and where each stage stands
Legend: ✅ done · 🟡 in progress · ⬜ not started

| Stage | What it means | Status |
|------|----------------|:--:|
| **1. Harness** | costs/backtest/walkforward/metrics; no-lookahead verified | ✅ |
| **2. Real data in** | adjusted daily bars via `fetch_data.py` (yfinance) or `fetch_alpaca.py` | 🟡 (6 test tickers exist; real liquid universe not chosen yet) |
| **3. First reasoned strategy** | Jonathan writes a thesis with a *why*; Tenzing implements it | ⬜ **(the current bottleneck)** |
| **4. Run + verdict** | run harness on a liquid ticker, record OOS-net-of-costs vs SPY | ⬜ |
| **5. Web app v1** | Next.js + FastAPI visualizer; restyle to `webapp/MOCKUP.html` | 🟡 (works; ugly — mockup is the target) |
| **6. Kronos for real** | run `forecast_kronos.py` non-mock on real tickers, read OOS row | ⬜ |
| **7. Paper trade survivors** | only a strategy that passes stage 4 → `alpaca_paper.py` for weeks | ⬜ |
| **8. Real money** | deferred decision; nothing until a survivor proves out on paper | ⬜ |

## The one thing blocking everything
**No reasoned strategy has been run through the harness on a real liquid ticker yet.** Tooling
(brokers, Notion, data vendors) is mostly decided. The unlock is stage 3 → 4, not more setup.

## Stack (decided)
- **Broker/data:** Alpaca (Trading API, paper). Shared paper account via API keys. Setup: [[plan/08-alpaca-setup]].
- **Data:** yfinance or Alpaca, daily, split/dividend-adjusted. Liquid equities/ETFs first (SPY/QQQ/IWM + large caps).
- **Holding style:** swing (daily bars, hold days–weeks). Intraday = researched phase-2.
- **Repo:** GitHub `10zinglunn-afk/tjh-trading`, branch `feat/webapp-v1`. Web app on Vercel; Supabase later (Phase B).
- **Collaboration:** Notion as the front door for Jonathan & Henry (theses, tasks, verdict view); repo canonical for code.

## Who's doing what next
- **Tenzing:** choose + fetch the liquid universe; restyle web app to the mockup; wire Notion; (optional) build verdict auto-logger.
- **Jonathan:** first strategy thesis in `/research/` (the bottleneck — unblocks stages 3–4).
- **Henry:** real cost table (bps per instrument) + tradable universe + interpret/benchmark verdicts. (Mechanical logging is being automated — see [[plan/01-decision-log]].)

## Open questions still on the table
- Equities-first vs push toward options sooner (team call, not yet ratified by J & H).
- If/when real money ever enters (deferred).
- Multiple-testing correction (deflated Sharpe / trial count) before scaling the universe.
