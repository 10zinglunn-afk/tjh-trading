"""Cross-sectional momentum panel backtest -- Thesis 001 (Jonathan).

The single-name engine (backtest.py) scores one ticker at a time; cross-sectional
momentum needs the whole panel at once: each month, rank every stock by its 12-1
trailing return (12 months back, skipping the most recent month) and hold the top
names equal-weight. Economic story: intermediate-horizon winners keep winning
(Jegadeesh-Titman 1993) via investor underreaction / slow information diffusion.

Honesty rails (same skeptic's bar as scan.py):
  * No lookahead: weights decided at month-end t are HELD from t+1 (weights.shift(1)),
    identical to the engine convention.
  * Net of the LIQUID-ETF cost regime (3/1 bps) on FULL portfolio turnover.
  * Canonical spec only (12-1, monthly, top 10, long-only). n_trials=1 -- we do not
    grid-search the thesis; a searched thesis is a different (weaker) claim.
  * Three baselines through the SAME dates and costs:
      - SPY buy&hold (the opportunity-cost bar),
      - equal-weight ALL eligible stocks (was it selection skill, or just the universe?),
      - random top-N picks each month (would any 10 names have worked?).
  * LOUD survivorship caveat: the universe is today's liquid names, so every ticker
    "survived" by construction. That inflates all long-only results here, including
    the baselines -- which is exactly why beating the EW-universe is the bar that
    matters most, not beating SPY.

    python3 xsect.py                # run Thesis 001 on realdata/
"""
import glob
import os
import sys

import numpy as np
import pandas as pd

from costs import CostModel
from data import load_csv
from metrics import compute_metrics
from diagnostics import deflated_sharpe_ratio, regime_split

ETF_COST = CostModel(spread_bps=3, slippage_bps=1)
# The benchmark and pure index/leveraged products are not cross-sectional candidates.
EXCLUDE = {'spy', 'qqq', 'dia', 'iwm', 'vti', 'tqqq'}
TOP_N = 10
LOOKBACK, SKIP = 252, 21       # canonical 12-1 in daily bars


def load_panel(paths):
    """Outer-join the close series of every CSV into one (dates x tickers) panel."""
    closes = {}
    for p in paths:
        t = os.path.splitext(os.path.basename(p))[0]
        closes[t] = load_csv(p, warn=False)['close']
    return pd.DataFrame(closes).sort_index()


def momentum_12_1(panel, lookback=LOOKBACK, skip=SKIP):
    """Score[t, name] = return from t-lookback to t-skip. NaN until enough history."""
    past = panel.shift(skip)
    return past / past.shift(lookback - skip) - 1.0


def month_end_mask(index):
    """True on the last trading day of each calendar month in the index."""
    s = pd.Series(1, index=index)
    last = s.groupby([index.year, index.month]).tail(1).index
    return index.isin(last)


def target_weights(panel, top_n=TOP_N, picker=None):
    """Daily target-weight DataFrame: at each month-end, long the top_n names by 12-1
    momentum (equal weight), hold until the next rebalance. `picker` overrides the
    selection (used by the random baseline); it gets (scores_row) -> list of names."""
    scores = momentum_12_1(panel)
    rebal = month_end_mask(panel.index)
    w = pd.DataFrame(np.nan, index=panel.index, columns=panel.columns)
    for t in panel.index[rebal]:
        row = scores.loc[t].dropna()
        if len(row) < top_n:            # not enough names with a full year of history yet
            continue
        names = picker(row) if picker else row.nlargest(top_n).index
        wt = pd.Series(0.0, index=panel.columns)
        wt[list(names)] = 1.0 / top_n
        w.loc[t] = wt
    return w.ffill().fillna(0.0)


def run_panel(panel, weights, cost_model=ETF_COST):
    """Panel analog of run_backtest: same shift(1) no-lookahead, same cost math,
    output shaped so compute_metrics works unchanged."""
    rets = panel.pct_change(fill_method=None).fillna(0.0)
    held = weights.shift(1).fillna(0.0)
    turnover = (weights - weights.shift(1)).abs().sum(axis=1).fillna(0.0)
    gross = (held * rets).sum(axis=1)
    cost = pd.Series(cost_model.cost_fraction(turnover.values), index=panel.index)
    net = gross - cost
    out = pd.DataFrame({'ret': gross, 'turnover': turnover, 'gross': gross,
                        'cost': cost, 'net': net, 'held': held.abs().sum(axis=1)})
    out['equity'] = (1 + net).cumprod()
    return out


def _first_active(df):
    """Trim the warm-up (weights all zero) so metrics reflect only the live period."""
    live = df.index[df['held'] > 0]
    return df.loc[live[0]:] if len(live) else df


def _pct(v):
    return f"{v * 100:8.1f}%" if v == v else '     nan'


def main():
    paths = sys.argv[1:] or sorted(glob.glob('realdata/*.csv'))
    stock_paths = [p for p in paths
                   if os.path.splitext(os.path.basename(p))[0] not in EXCLUDE]
    if not stock_paths:
        print("No stock CSVs found. Run fetch_universe.py first.")
        return
    panel = load_panel(stock_paths)

    # Thesis 001, canonical spec.
    res = _first_active(run_panel(panel, target_weights(panel)))
    window = res.index

    # Baseline 1: hold SPY over the identical live window (net of the same cost model).
    spy_close_full = (load_csv('realdata/spy.csv', warn=False)['close']
                      if os.path.exists('realdata/spy.csv') else None)
    spy_m = None
    if spy_close_full is not None:
        spy = spy_close_full.reindex(window).dropna()
        spy_pos = pd.Series(1.0, index=spy.index)
        from backtest import run_backtest
        _, spy_m = run_backtest(spy, spy_pos, ETF_COST)

    # Baseline 2: equal-weight ALL eligible names (the universe itself, same costs).
    scores = momentum_12_1(panel)
    rebal = month_end_mask(panel.index)
    ew = pd.DataFrame(np.nan, index=panel.index, columns=panel.columns)
    for t in panel.index[rebal]:
        row = scores.loc[t].dropna()
        if len(row) < TOP_N:
            continue
        wt = pd.Series(0.0, index=panel.columns)
        wt[row.index] = 1.0 / len(row)
        ew.loc[t] = wt
    ew_res = _first_active(run_panel(panel, ew.ffill().fillna(0.0)))
    ew_res = ew_res.reindex(window).dropna()

    # Baseline 3: random TOP_N picks each month, same machinery and costs.
    rng = np.random.default_rng(1)
    rand_res = _first_active(run_panel(
        panel, target_weights(panel, picker=lambda row: rng.choice(
            row.index, size=TOP_N, replace=False))))
    rand_res = rand_res.reindex(window).dropna()

    m = compute_metrics(res)
    m_ew = compute_metrics(ew_res)
    m_rand = compute_metrics(rand_res)

    n_names = panel.shape[1]
    print(f"\nCROSS-SECTIONAL MOMENTUM (Thesis 001) -- 12-1, monthly, top {TOP_N} of "
          f"{n_names} stocks, long-only, equal weight")
    print(f"Live window: {window[0].date()} -> {window[-1].date()} "
          f"({len(window)} bars). Net of LIQUID-ETF costs (3/1 bps) on full turnover. "
          f"n_trials=1 (canonical spec, no grid).\n")
    hdr = f"  {'portfolio':22s} {'total ret':>10s} {'CAGR':>8s} {'Sharpe':>7s} {'maxDD':>8s} {'trades':>7s}"
    print(hdr)
    print("  " + "-" * 68)

    def line(name, mm):
        print(f"  {name:22s} {_pct(mm['total_return'])} {mm['cagr']*100:7.1f}% "
              f"{mm['sharpe']:7.2f} {_pct(mm['max_drawdown'])} {mm['num_trades']:7d}")

    line('momentum top-10', m)
    line('EW universe (all)', m_ew)
    line('random top-10', m_rand)
    if spy_m is not None:
        line('hold SPY', spy_m)

    # Per-year split: a one-year-wonder is the classic way a fake edge hides.
    print("\nPer-year net return (momentum vs EW universe -- selection skill by year):")
    for yr, g in res.groupby(res.index.year):
        mo = (1 + g['net']).prod() - 1
        ge = ew_res.reindex(g.index).dropna()
        ewr = (1 + ge['net']).prod() - 1 if len(ge) else float('nan')
        mark = '+' if mo > ewr else '-'
        print(f"    {yr}: momentum {_pct(mo)}   EW {_pct(ewr)}   [{mark}]")

    # ROBUSTNESS GAUNTLET -- the same skeptic's checks the single-name scan applies, so the
    # one surviving candidate is scrutinised BEFORE any human signs off on it.
    # (1) Probabilistic Sharpe on MONTHLY returns. This is a monthly strategy; scoring its
    #     Sharpe on daily bars would count ~21 held-flat days as 21 independent observations
    #     and overstate significance. Monthly returns are the honest, ~independent unit.
    monthly = res['net'].groupby([res.index.year, res.index.month]).apply(
        lambda x: (1 + x).prod() - 1)
    psr = deflated_sharpe_ratio(monthly.values, n_trials=1, ppy=12)   # n=1 => P(Sharpe > 0)
    # (2) Regime split: is the "edge" just a bull-market ride?
    regimes = regime_split(res['net'], spy_close_full) if spy_close_full is not None else None

    print("\nROBUSTNESS (same gauntlet as the scan):")
    print(f"  Probabilistic Sharpe (monthly, {len(monthly)} months): "
          f"{psr:.2f}  (P the true Sharpe is > 0; >=0.95 = significant)")
    if regimes:
        print("  Net return by SPY regime (a long-only signal is expected to lean 'up'):")
        for r in ('up', 'down', 'chop'):
            print(f"    {r:4s}: {_pct(regimes[r]['return'])}  ({regimes[r]['bars']} bars)")

    flags = []
    if psr == psr and psr < 0.95:
        flags.append(f"Probabilistic Sharpe {psr:.2f} < 0.95 -- not clearly distinguishable from zero.")
    yearly = [(y, (1 + g['net']).prod() - 1) for y, g in res.groupby(res.index.year)]
    ylogs = [(y, np.log(1 + r)) for y, r in yearly if r > -1]
    ytot = sum(l for _, l in ylogs)
    if ytot > 0 and ylogs:
        by, bl = max(ylogs, key=lambda t: t[1])
        if bl / ytot > 0.6:
            flags.append(f"{bl/ytot*100:.0f}% of the (log) return came from {by} -- a one-year wonder.")
    if regimes:
        worst = min(('up', 'down', 'chop'), key=lambda r: regimes[r]['return'])
        if regimes[worst]['return'] < -0.05:     # materially loses money in some regime
            flags.append(f"Loses in the '{worst}' regime ({_pct(regimes[worst]['return']).strip()}) "
                         f"-- momentum leans on 'up' markets and whipsaws in chop, not all-weather.")
    if flags:
        print("  RED FLAGS:")
        for f in flags:
            print(f"    - {f}")
    else:
        print("  No robustness red flag fired (the survivorship caveat below still stands).")

    print("\nThe bar that matters:")
    beats_ew = m['total_return'] > m_ew['total_return']
    beats_rand = m['total_return'] > m_rand['total_return']
    beats_spy = spy_m is None or m['total_return'] > spy_m['total_return']
    print(f"  beats EW universe:  {'YES' if beats_ew else 'NO'}   "
          f"(selection skill vs just owning these names)")
    print(f"  beats random picks: {'YES' if beats_rand else 'NO'}")
    print(f"  beats holding SPY:  {'YES' if beats_spy else 'NO'}")

    print("\nCAVEATS (read before believing anything above):")
    print(f"  * SURVIVORSHIP: the universe is today's {n_names} liquid names -- every one")
    print("    survived to 2026 by construction. This inflates ALL long-only rows above,")
    print("    which is why 'beats EW universe' is the honest bar, not the raw return.")
    print("  * Single history, no folds: there is nothing to fit (n_trials=1), but this is")
    print("    still ONE draw of history -- the per-year split, regime split, and probabilistic")
    print("    Sharpe above ARE that scrutiny; a live paper-trade is the real out-of-sample test.")
    if beats_ew and beats_rand and beats_spy:
        rob = ('robustness-checked with no red flag' if not flags
               else f'but {len(flags)} robustness flag(s) above temper it')
        verdict = (f'SURVIVES the panel bar; {rob}. '
                   f'Awaiting Jonathan sign-off (economic story) + Henry judgment.')
    else:
        verdict = 'DOES NOT clear the bar -- selection added nothing beyond the universe'
    print(f"\nVERDICT: {verdict}\n")


if __name__ == '__main__':
    main()
