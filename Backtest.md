---
tags: [algo-trading, backtest]
source: backtest.py
---
# Backtest Engine

Bar-by-bar backtest with **no lookahead**.

> [!warning] The most common way beginners cheat by accident
> They let a position earn the *same bar's* return — i.e. they act on information
> they wouldn't have had yet. Here, no-lookahead is **baked into the engine**, not
> trusted to each [[Strategies|strategy]].

## The convention
`positions[t]` is the target weight decided using information available **up to and
including bar `t`'s close**. The return you actually earn on bar `t` is the position
you were **already holding** (decided at `t-1`) times bar `t`'s return.

That is enforced by one line:

```python
held = positions.shift(1)   # <-- no lookahead
```

So: decide at `t`, earn at `t+1`. Always.

## Turnover
Turnover is how much the position changed — the thing [[Costs]] charges against:

$$\text{turnover}_t = \lvert \text{pos}_t - \text{pos}_{t-1} \rvert$$

The first bar uses `|pos|` (entering a position is itself a trade you pay for).

## Code
```python
import pandas as pd
from metrics import compute_metrics


def run_backtest(prices, positions, cost_model, periods_per_year=252):
    prices = prices.astype(float)
    rets = prices.pct_change().fillna(0.0)
    pos = positions.reindex(prices.index).fillna(0.0).clip(-1, 1)
    held = pos.shift(1).fillna(0.0)                       # <-- no lookahead
    turnover = (pos - pos.shift(1)).abs().fillna(pos.abs())
    costs = pd.Series(cost_model.cost_fraction(turnover.values), index=prices.index)
    gross = held * rets
    net = gross - costs
    out = pd.DataFrame({'ret':rets,'pos':pos,'held':held,'turnover':turnover,
                        'gross':gross,'cost':costs,'net':net})
    out['equity'] = (1 + net).cumprod()
    return out, compute_metrics(out, periods_per_year)
```

`net = gross − cost` is the only return that means anything. Equity compounds `net`.

## See also
- [[Costs]] — `cost_model.cost_fraction` consumes the turnover computed here
- [[Metrics]] — `compute_metrics` turns this DataFrame into Sharpe/DD/etc.
- [[Strategies]] — produce the `positions` Series fed in
- [[Walkforward]] — calls `run_backtest` once per parameter set
