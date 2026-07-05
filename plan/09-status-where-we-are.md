# 09 — STATUS: Where We Are (living tracker)

Home: [[PROJECT_PLAN]] · Charter: [[plan/07-charter-what-we-do]] · Decisions: [[plan/01-decision-log]]

*The single "where are we right now" page. Update this whenever a stage moves. If you (or
Claude) are catching up cold, read this first, then the charter. Last updated: 2026-07-05.*

## The mission, in one line
Find ONE signal that beats buy-and-hold OOS net of realistic costs on real equity data, prove
it honestly, and make the proof visible. We have **zero survivors so far** — that's expected.

## The pipeline and where each stage stands
Legend: ✅ done · 🟡 in progress · ⬜ not started

| Stage | What it means | Status |
|------|----------------|:--:|
| **1. Harness** | costs/backtest/walkforward/metrics; no-lookahead verified | ✅ |
| **2. Real data in** | adjusted daily bars via `fetch_data.py` (yfinance) or `fetch_alpaca.py` | 🟡 (~100-ticker liquid universe fetched via `fetch_universe.py` (broadened from 53 on 2026-07-05); Henry to ratify) |
| **3. First reasoned strategy** | Jonathan writes a thesis with a *why*; Tenzing implements it | 🟡 (Thesis 001 IMPLEMENTED + RUN 2026-07-03 — `xsect.py` panel engine + `time_series_momentum`; **awaiting Jonathan's signature** to close the loop) |
| **4. Run + verdict** | run harness on a liquid ticker, record OOS-net-of-costs vs SPY | 🟡 (Thesis 001 **SURVIVES the panel bar** — +972% vs +265% EW-universe on ~90 names, won 5/8 years, see [[plan/02-verdict-log]]; **robustness-checked 2026-07-05**: monthly PSR 1.00, **9/9 sensitivity-sweep neighbors beat EW** (edge is broad), but regime split flags −39% in chop → bull-market vehicle; wide scan v3: 0/309 clean single-name edges. Henry's judgment + Jonathan sign-off before ADVANCE) |
| **5. Web app v1** | Next.js + FastAPI visualizer; restyle to `webapp/MOCKUP.html` | ✅ (LIVE full-stack: https://webapp-zeta-liart.vercel.app + Render backend. 2026-07-03: restyled to mockup, defaults to real SPY, shows the real track record + Thesis 001) |
| **6. Kronos for real** | run `forecast_kronos.py` non-mock on real tickers, read OOS row | ⏸️ **PARKED** — Kronos is strongest *intraday*; we trade *daily swing*. Only revisit if we ever choose to go intraday (phase-2 scope change, not made). See [[plan/01-decision-log]]. |
| **7. Paper trade survivors** | only a strategy that passes stage 4 → `alpaca_paper.py` for weeks | ⬜ |
| **8. Real money** | deferred decision; nothing until a survivor proves out on paper | ⬜ |

## The one thing blocking everything
**Human sign-offs, not the machine.** The first reasoned strategy (Thesis 001,
cross-sectional momentum) is implemented AND run — it survives its first panel test.
What's missing is people: Jonathan signs the thesis, Henry judges the verdict
(real-or-survivorship), then paper trading via `alpaca_paper.py` (needs Alpaca keys).

## Stack (decided)
- **Broker/data:** Alpaca (Trading API, paper). Shared paper account via API keys. Setup: [[plan/08-alpaca-setup]].
- **Data:** yfinance or Alpaca, daily, split/dividend-adjusted. Liquid equities/ETFs first (SPY/QQQ/IWM + large caps).
- **Holding style:** swing (daily bars, hold days–weeks). Intraday = researched phase-2.
- **Repo:** GitHub `10zinglunn-afk/tjh-trading`, branch `main` (feat/webapp-v1 merged 2026-07-02; work merges to main same session it stops). Web app on Vercel; Supabase later (Phase B).
- **Collaboration:** Notion as the front door for Jonathan & Henry (theses, tasks, verdict view); repo canonical for code.

## Who's doing what next
- **Tenzing:** ✅ universe · ✅ Notion · ✅ auto-logger · ✅ full-stack deploy (2026-07-03) · ✅ mockup restyle · ✅ tsmom + `xsect.py` panel engine built and run (2026-07-03). Left: get Jonathan + Henry to act (below); add Alpaca paper keys; tell Notion the news.
- **Jonathan:** SIGN Thesis 001 (it's pre-filled AND now has a run + surviving verdict attached — he reviews the economic story and owns or amends it).
- **Henry:** real cost table (bps per instrument) + tradable universe + interpret/benchmark verdicts. (Mechanical logging is being automated — see [[plan/01-decision-log]].)

## Open questions still on the table
- Equities-first vs push toward options sooner (team call, not yet ratified by J & H).
- If/when real money ever enters (deferred).
- Multiple-testing correction (deflated Sharpe / trial count) before scaling the universe.
