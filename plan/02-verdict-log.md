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
| 2026-07-03 | **Thesis 001: cross-sectional 12-1 momentum** (monthly, top 10 EW, long-only, n_trials=1) | ~92 stocks (universe minus ETFs), daily, 2019-08→2026-07 | Liquid ETF 3/1 on full turnover | **+972%** (CAGR 41.0%, Sharpe 1.21) | beat SPY (+180%), **EW-universe (+265%)** and random (+250%); won 5/8 years incl. 2022 (−2.4% vs −13.4%) | **ITERATE → paper?** | First *reasoned* strategy ever run (`xsect.py`, panel engine). Cleared the honest bar (selection skill beyond the survivor universe). **Universe broadened 47 → ~90 liquid names (2026-07-05) — result held.** Caveats: survivorship-biased universe, single history. **Robustness gauntlet (`xsect.py` + `diagnostics.py`):** monthly probabilistic Sharpe **1.00**; a **sensitivity sweep** of the canonical spec's neighbors (6/9/12-mo × top 5/10/15) has **9/9 beat their EW-universe** → the edge is broad, not a knife-edge config (reported as robustness, NOT selection). BUT the regime split **flags it: −39.1% in chop** (up +1695% / down −2.0% / chop −39.1%) → a bull-market vehicle, not all-weather. **Needs Jonathan's sign-off + Henry's judgment before ADVANCE.** |
| 2026-07-05 | **Wide scan v3**: SMA + mean-rev + ts-momentum grids | ~100 liquid US tickers (universe broadened), daily, ~8y | Liquid ETF 3/1 + SPY gate + deflated Sharpe | **0 survivors** | 309 backtests → 0 EDGE?, 38 suspect, 271 dead | **KILL (all single-name)** | Universe broadened 53 → ~100 names. Still zero clean single-name edges after all four gates — the honest base rate holds at scale, and remains the argument *for* the cross-sectional (panel) version above. |
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
