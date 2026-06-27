"""Entry point. Runs baselines + a candidate strategy under several cost regimes,
then a walk-forward (out-of-sample) test.

    python run.py            # synthetic data (always works)
    python run.py spy.csv    # real data fetched locally via fetch_data.py
"""
import os
import sys
import pandas as pd
from data import synthetic_ohlcv, load_csv
from costs import CostModel
from backtest import run_backtest
from metrics import compute_metrics
from strategies import (buy_and_hold, random_strategy, sma_crossover,
                        mean_reversion, kronos_signal)
from walkforward import walk_forward


def load_kronos_forecast(path):
    """If a forecast_kronos.py sidecar (<stem>.kronos.csv) exists next to the price
    CSV, load its pred_ret column. Returns None if absent (Kronos rows are skipped)."""
    if not path:
        return None
    sidecar = path.rsplit(".", 1)[0] + ".kronos.csv"
    if not os.path.exists(sidecar):
        return None
    fc = pd.read_csv(sidecar, parse_dates=[0], index_col=0)["pred_ret"]
    print(f"(loaded Kronos forecast: {sidecar}, {int(fc.notna().sum())} forecasts)\n")
    return fc


def fmt(m):
    f = lambda v, s='6.1f': (format(v * 100, s) if v == v else ' nan')
    return (f"ret={f(m['total_return'])}%  Sharpe={m['sharpe']:5.2f}  "
            f"maxDD={f(m['max_drawdown'])}%  trades={m['num_trades']:4d}  "
            f"win={f(m['win_rate'],'4.1f')}%")


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else None
    if path:
        df = load_csv(path); src = f"REAL data: {path}"
    else:
        # mild edge baked in so we see the full pipeline; real markets are much closer to kappa=0
        df = synthetic_ohlcv(n=1500, kappa=0.04)
        src = "SYNTHETIC (kappa=0.04 edge baked in). Sandbox has no internet; use fetch_data.py for SPY/QQQ."
    px = df['close']
    print(f"Data: {src}\nbars={len(px)}\n")

    forecast = load_kronos_forecast(path)

    regimes = [
        ('FRICTIONLESS (the lie)',     CostModel(spread_bps=0,   slippage_bps=0)),
        ('LIQUID ETF (SPY-like)',      CostModel(spread_bps=3,   slippage_bps=1)),
        ('CHEAP OPTION spread',        CostModel(spread_bps=300, slippage_bps=50)),
    ]
    strats = {
        'buy_and_hold': (buy_and_hold, {}),
        'random':       (random_strategy, {'seed': 1}),
        'sma_20_100':   (sma_crossover, {'fast': 20, 'slow': 100}),
        'meanrev_20_1': (mean_reversion, {'lookback': 20, 'entry_z': 1.0}),
    }
    if forecast is not None:
        strats['kronos'] = (kronos_signal, {'forecast': forecast, 'threshold': 0.0})
    for label, cm in regimes:
        print(f"=== {label} ===")
        for name, (fn, kw) in strats.items():
            _, m = run_backtest(px, fn(px, **kw), cm)
            print(f"  {name:14s} {fmt(m)}")
        print()

    print("=== WALK-FORWARD: mean reversion, params chosen OUT-OF-SAMPLE, ETF costs ===")
    grid = [{'lookback': lb, 'entry_z': z}
            for lb in (10, 20, 40) for z in (0.5, 1.0, 1.5, 2.0)]
    factory = lambda p: (lambda prices: mean_reversion(prices, **p))
    combined, chosen = walk_forward(px, factory, grid, CostModel(3, 1), n_folds=5)
    m = compute_metrics(combined)
    print(f"  OOS combined   {fmt(m)}")
    print(f"  params/fold:   {[ (c['lookback'], c['entry_z']) for c in chosen ]}")

    if forecast is not None:
        print("\n=== WALK-FORWARD: KRONOS, threshold chosen OUT-OF-SAMPLE, ETF costs ===")
        kgrid = [{'threshold': th} for th in (0.0, 0.001, 0.003, 0.005, 0.01)]
        kfactory = lambda p: (lambda prices: kronos_signal(prices, forecast=forecast, **p))
        kcomb, kchosen = walk_forward(px, kfactory, kgrid, CostModel(3, 1), n_folds=5)
        km = compute_metrics(kcomb)
        print(f"  OOS combined   {fmt(km)}")
        print(f"  thresh/fold:   {[c['threshold'] for c in kchosen]}")

    print("\n(OOS = out-of-sample: the only row that isn't lying to you.)")


if __name__ == '__main__':
    main()
