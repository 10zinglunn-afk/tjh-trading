# 02 — Verdict Log (the track record)

Home: [[PROJECT_PLAN]] · Owner: **Henry** (with Tenzing's harness output)

*This is the club's actual research record and our most valuable asset. One row per test.
Newest first. The point is honesty: most rows will say "no edge." That's the truth working.*

## How to read a row
- **OOS net** = out-of-sample walk-forward return, net of `costs.py`. The only number that matters.
- **vs SPY** = same-window buy-and-hold SPY return. If we didn't beat this, active trading lost.
- **Verdict** = KILL / ITERATE / ADVANCE (to paper) — never "trust me."

| Date | Strategy | Data (ticker / freq / window) | Cost regime | OOS net | vs SPY | Verdict | Notes |
|------|----------|-------------------------------|-------------|---------|--------|---------|-------|
| 2026-07-03 | **Thesis 001: cross-sectional 12-1 momentum** (monthly, top 10 EW, long-only, n_trials=1) | 47 stocks (universe minus ETFs), daily, 2019-08→2026-06 | Liquid ETF 3/1 on full turnover | **+756%** (CAGR 36.6%, Sharpe 1.20) | beat SPY (+181%), **EW-universe (+298%)** and random picks (+291%); won 5/8 years incl. 2022 (−4.9% vs −20.8%) | **ITERATE → paper?** | First *reasoned* strategy ever run (`xsect.py`, new panel engine). Cleared the honest bar (selection skill beyond the survivor universe). Caveats: survivorship-biased universe, single history. **Robustness gauntlet (2026-07-05, `xsect.py`):** monthly probabilistic Sharpe **1.00** (distinguishable from zero at the honest monthly frequency), but the regime split **flags it: −34.8% in chop** (up +1205% / down +0.6% / chop −34.8%) → a bull-market vehicle, not all-weather. **Needs Jonathan's sign-off + Henry's judgment before ADVANCE.** |
| 2026-07-03 | **Wide scan v2**: SMA + mean-rev + **ts-momentum** grids (N=159 trials) | 53 liquid US tickers, daily, ~8y | Liquid ETF 3/1 + SPY gate + deflated Sharpe | **0 survivors** | tsmom dominates the suspect tier (23 suspects) | **KILL (all single-name)** | `tsmom` added to the library. Single-name momentum fails the gates exactly as theory predicts (too few trades/name, 2020-heavy) — which is the argument *for* the cross-sectional version above. |
| 2026-06-30 | **Wide scan**: SMA + mean-rev param grids (N=106 trials) | 53 liquid US tickers, daily, ~8y | Liquid ETF 3/1 + SPY gate + deflated Sharpe | **0 survivors** | none beat SPY cleanly | **KILL (all)** | `scan.py` first full run. 12 "suspects" flagged; every one failed ≥1 honesty gate (thin trades / one-regime / DSR < 0.95). This is the honest base rate — logged 2026-07-02 by Tenzing; Henry to countersign judgment. |
| 2026-06-12 | Baselines (SMA, mean-rev, random) | 6 real tickers, daily, 2018–2026 | Liquid ETF 3/1 | — | — | KILL | None beat buy-and-hold OOS after costs (from project notes). |
| _pending_ | Kronos zero-shot | 6 real tickers, daily | Liquid ETF 3/1 | _run for real_ | | _pending_ | Expectation: fails on daily bars. Run locally, not --mock. **2026-07-02: forecast alignment bug fixed first** (context slice skipped bar t) — good thing we didn't run before the fix. |

## Standing expectations (so we're not surprised)
- Daily-bar strategies mostly die after costs. Kronos is strongest intraday.
- Options regime (300/50 bps) eats almost any active edge → expect ~−100% for naive options.

## Machine log
Every real `run.py <ticker.csv>` walk-forward now auto-appends to `verdicts.jsonl`
(`verdict_log.py`, plan/10 Part A). Render it here with
`python3 verdict_log.py --write-md plan/02-verdict-log.md` — the table lands below the
marker; everything above stays human-owned. Henry fills only the **Judgment** column.

<!-- AUTO-VERDICTS BELOW: rendered by verdict_log.py, do not hand-edit -->

| Date | Strategy | Data | Cost regime | OOS net | OOS Sharpe | vs B&H | vs SPY | Flags | Judgment (Henry) |
|------|----------|------|-------------|---------|-----------|--------|--------|-------|------------------|
| 2026-07-03 | meanrev_wf | spy | 3/1 bps (liquid ETF) | +28.2% | 0.55 | lost | +166.7% | 1 flag(s) | |
