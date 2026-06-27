---
tags: [algo-trading, backtest]
source: run.py
---
# Run — Entry Point

Wires everything together: runs the baselines + a candidate strategy under several
[[Costs|cost regimes]], then a [[Walkforward|walk-forward]] (out-of-sample) test, and
prints the comparison table.

## Usage
```bash
python3 run.py            # synthetic data (always works)
python3 run.py spy.csv    # real data, fetched locally via fetch_data.py
```

With no argument it uses the [[Data|synthetic]] fixture with a mild edge baked in
(`kappa=0.04`) so you can watch the full pipeline. Real markets are much closer to
`kappa=0` (no edge).

## What it prints
For each of the three regimes — FRICTIONLESS, LIQUID ETF, CHEAP OPTION — it scores
four [[Strategies|strategies]]: `buy_and_hold`, `random`, `sma_20_100`, `meanrev_20_1`.
Then one walk-forward row where mean-reversion parameters are chosen **out-of-sample**.

> [!tip] Reading the output
> - **FRICTIONLESS** = the lie. Raw signal only.
> - **LIQUID ETF** = the truth for stocks.
> - **CHEAP OPTION** = why frequent options trading → ~−100%.
> - **OOS combined** = the only row that isn't lying to you.

## Code
```python
import sys
import pandas as pd
from data import synthetic_ohlcv, load_csv
from costs import CostModel
from backtest import run_backtest
from metrics import compute_metrics
from strategies import buy_and_hold, random_strategy, sma_crossover, mean_reversion
from walkforward import walk_forward


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
    print("\n(OOS = out-of-sample: the only row that isn't lying to you.)")


if __name__ == '__main__':
    main()
```

## See also
- [[Data]] — synthetic fixture + CSV loader feeding `px`
- [[Costs]] — the three regimes
- [[Strategies]] — the four candidates scored
- [[Backtest]] / [[Metrics]] — engine + scoring
- [[Walkforward]] — the out-of-sample row
