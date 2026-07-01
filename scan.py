"""Wide scan -- run the curated strategy library across a whole universe of tickers
and rank the results, HONESTLY.

Philosophy (plan/11): scan wide to DISCOVER candidates, demand a high bar to BELIEVE one.
This file is a thin convenience wrapper over the canonical engine -- it loops
walk_forward() over (ticker x strategy x param-grid) and collects the OUT-OF-SAMPLE,
net-of-costs result for each. It does NOT reimplement costs/backtest/walkforward, and
it introduces no new backtest math.

What it answers: "over a basket of stocks, where (if anywhere) does a strategy's timing
actually beat just holding the index (SPY) out-of-sample, after costs -- and which name is
worth a closer look?" Each ticker is scored independently (no cross-asset coupling), so this
is just a loop; it needs no multi-asset engine.

Honesty rails baked in:
  * Gate 1 -- every number is net of the LIQUID-ETF cost regime (3/1 bps), not frictionless.
  * Gate 2 -- buy&hold, random AND (if realdata/spy.csv exists) holding SPY over the same
              window are all scored on the identical OOS dates, so "beats them" is real.
  * Gate 3 -- the trial count N (grid size searched) is printed next to every result, so a
              big-looking Sharpe that is really "best of 12" is visible. (Full deflated
              Sharpe lives in the diagnostics module; N is the minimum bar plan/11 requires.)
  * Gate 4 -- trades/fold is shown and flagged when < 30 (too few trades = luck, not edge).

    python scan.py                       # scan every realdata/*.csv
    python scan.py realdata/tqqq.csv f.csv  # scan a chosen subset
"""
import glob
import os
import sys
import time

from data import load_csv
from costs import CostModel
from metrics import compute_metrics
from strategies import buy_and_hold, random_strategy, sma_crossover, mean_reversion
from walkforward import walk_forward

# The truth-for-equities regime. Frictionless is a lie; options are a separate study.
ETF_COST = CostModel(spread_bps=3, slippage_bps=1)
N_FOLDS = 5
MIN_TRADES_PER_FOLD = 30           # Gate-4 flag: fewer than this per fold => suspect

# Candidate signals we actually scan (economically distinct families only, per plan/11).
CANDIDATES = {
    'sma':     (sma_crossover,
                [{'fast': f, 'slow': s} for f in (10, 20, 50) for s in (100, 150, 200)]),
    'meanrev': (mean_reversion,
                [{'lookback': lb, 'entry_z': z}
                 for lb in (10, 20, 40) for z in (0.5, 1.0, 1.5, 2.0)]),
}
# Baselines -- the bar every candidate must clear, run through the SAME folds.
BASELINES = {
    'buy_hold': (buy_and_hold, [{}]),
    'random':   (random_strategy, [{'seed': 1}]),
}


def _factory(fn):
    """Adapt a signal fn to walk_forward's strat_factory(params) -> (prices -> positions)."""
    return lambda params: (lambda prices: fn(prices, **params))


def _oos(px, fn, grid, cost_model=ETF_COST, n_folds=N_FOLDS):
    """Walk-forward one (signal, grid) on a price series; return (OOS metrics, OOS index).
    The OOS index is identical across strategies on a ticker (folds depend only on length),
    so callers reuse the buy&hold run's index as the ticker's OOS window."""
    combined, _ = walk_forward(px, _factory(fn), grid, cost_model, n_folds=n_folds)
    m = compute_metrics(combined)
    m['n_trials'] = len(grid)
    return m, combined.index


def scan_universe(paths, benchmark=None, cost_model=ETF_COST, n_folds=N_FOLDS):
    """Loop the curated library over a universe. Returns a list of result dicts, one per
    (ticker, candidate strategy). Each carries its OOS-net-of-costs metrics and the bars it
    is judged against: the ticker's own buy&hold + random (through the same folds) and, if a
    `benchmark` close Series (SPY) is given, the return of just HOLDING SPY over the identical
    OOS window -- the opportunity-cost bar the charter treats as canonical."""
    rows = []
    for path in paths:
        ticker = os.path.splitext(os.path.basename(path))[0]
        px = load_csv(path)['close']
        base, oos_idx = {}, None
        for name, (fn, grid) in BASELINES.items():
            m, idx = _oos(px, fn, grid, cost_model, n_folds)
            base[name] = m
            if name == 'buy_hold':
                oos_idx = idx
        bh, rnd = base['buy_hold']['total_return'], base['random']['total_return']

        spy = None                              # hold-SPY total return over the same OOS window
        if benchmark is not None and oos_idx is not None and len(oos_idx):
            b = benchmark.reindex(oos_idx).dropna()
            if len(b) > 1:
                spy = float(b.iloc[-1] / b.iloc[0] - 1)

        for strat, (fn, grid) in CANDIDATES.items():
            m, _ = _oos(px, fn, grid, cost_model, n_folds)
            ret = m['total_return']
            tpf = m['num_trades'] / n_folds
            beats_bh = ret > bh
            beats_rnd = ret > rnd
            beats_spy = spy is None or ret > spy         # no SPY on disk => don't block on it
            survives_gate2 = beats_bh and beats_rnd
            # A clean look-closer must clear the REAL bar: beat holding SPY, beat random,
            # actually make money, and trade enough that it isn't 2-3 lucky rides.
            clean = (survives_gate2 and beats_spy and ret > 0
                     and tpf >= MIN_TRADES_PER_FOLD)
            rows.append({
                'ticker': ticker, 'strategy': strat, 'metrics': m,
                'bh_return': bh, 'rand_return': rnd, 'spy_return': spy,
                'beats_bh': beats_bh, 'beats_rand': beats_rnd, 'beats_spy': beats_spy,
                'survives_gate2': survives_gate2, 'clean': clean,
                'trades_per_fold': tpf, 'thin': tpf < MIN_TRADES_PER_FOLD,
            })
    return rows


def _pct(v, width=7):
    if v is None or v != v:
        return format('nan', f'>{width}') + ' '
    return format(v * 100, f'{width}.1f') + '%'


def _verdict(r):
    return ('EDGE?' if r['clean'] else
            'suspect' if r['survives_gate2'] else   # beat both baselines but thin/lost money
            'beats B&H' if r['beats_bh'] else 'dead')


HDR = "  ticker strat     N   OOS ret   Sharpe   maxDD   trds  t/fold    vsSPY  verdict"


def _line(r):
    m = r['metrics']
    flag = ' *thin' if r['thin'] else ''
    vs = _pct(m['total_return'] - r['spy_return'], 7) if r['spy_return'] is not None else '   n/a '
    return (f"  {r['ticker']:6s} {r['strategy']:7s} {m['n_trials']:3d} "
            f"{_pct(m['total_return'])}  {m['sharpe']:6.2f}  {_pct(m['max_drawdown'], 6)} "
            f"{m['num_trades']:5d} {r['trades_per_fold']:6.1f} {vs}  {_verdict(r)}{flag}")


def main():
    paths = sys.argv[1:] or sorted(glob.glob('realdata/*.csv'))
    if not paths:
        print("No CSVs to scan. Pass paths or run fetch_universe.py into realdata/.")
        return
    # SPY is the opportunity-cost benchmark ("would I have been better off in the index?").
    benchmark = None
    if os.path.exists('realdata/spy.csv'):
        benchmark = load_csv('realdata/spy.csv', warn=False)['close']

    t0 = time.time()
    rows = scan_universe(paths, benchmark=benchmark)
    elapsed = time.time() - t0

    tickers = sorted({r['ticker'] for r in rows})
    rows.sort(key=lambda r: (r['metrics']['total_return']
                             if r['metrics']['total_return'] == r['metrics']['total_return']
                             else -1e9), reverse=True)

    print(f"\nWIDE SCAN -- {len(tickers)} tickers x {len(CANDIDATES)} strategies "
          f"= {len(rows)} backtests, walk-forward OOS, net of LIQUID-ETF costs (3/1 bps), "
          f"{N_FOLDS} folds")
    bench = ("judged vs HOLDING SPY over the same window" if benchmark is not None
             else "(no realdata/spy.csv -> vsSPY blank)")
    print(f"{bench}.  Ran in {elapsed:.2f}s "
          f"({elapsed / max(len(rows), 1) * 1000:.0f} ms/backtest) -- compute is a non-issue.\n")

    edges = [r for r in rows if r['clean']]
    suspects = [r for r in rows if r['survives_gate2'] and not r['clean']]
    print(f"RESULT: {len(edges)} EDGE?  |  {len(suspects)} suspect  |  "
          f"{len(rows) - len(edges) - len(suspects)} dead   (of {len(rows)})\n")

    if edges:
        print("EDGE? candidates (beat SPY + random, positive, >=30 trades/fold):")
        print(HDR); print("  " + "-" * 82)
        for r in edges:
            print(_line(r))
        print()

    top_n = min(20, len(rows))
    print(f"TOP {top_n} by OOS net return (context -- most of these are noise):")
    print(HDR); print("  " + "-" * 82)
    for r in rows[:top_n]:
        print(_line(r))

    print("\n" + "-" * 86)
    if edges:
        top = edges[0]
        print(f"Closest look -> {top['ticker'].upper()} / {top['strategy']}: "
              f"OOS {_pct(top['metrics']['total_return'])} net, beats SPY + random, "
              f"{top['trades_per_fold']:.0f} trades/fold.")
        print("  Still a SUSPECT, not a winner. Before it is believed it needs:")
        print(f"  (Gate 3) a deflated Sharpe -- best of {top['metrics']['n_trials']} configs "
              f"across {len(tickers)} names; and")
        print("  (Gate 4) a Jonathan thesis for WHY the edge exists and who is on the other side.")
    else:
        print(f"No clean survivor in {len(rows)} backtests across {len(tickers)} liquid names.")
        print("Nothing beat SPY + random OOS after costs with a positive, non-thin record.")
        print("That is the honest base rate: on liquid daily bars, simple timing rules do not")
        print("beat just holding the index. The scan did its job by refusing a fake winner.")
    print("* thin = fewer than 30 trades/fold; treat its Sharpe as noise.\n")


if __name__ == '__main__':
    main()
