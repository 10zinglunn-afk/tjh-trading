# Backtest Harness — the skeptic's machine

A small, honest backtesting pipeline for evaluating trading strategies *net of realistic
costs*, with out-of-sample (walk-forward) validation. Built to **disprove** strategies,
not to flatter them. Goal of the project: turn $23 into more — but the real deliverable
is a system that tells you the truth about whether an edge exists.

## The one rule
A strategy is only "real" if it beats dumb baselines (buy-and-hold, random) **out-of-sample,
after costs.** Almost nothing does. That is the point.

## Files
| File | Job |
|------|-----|
| `costs.py` | Cost model: spread + slippage + fees in basis points. The most important file. |
| `backtest.py` | Bar-by-bar engine. Enforces **no lookahead** via `positions.shift(1)`. |
| `metrics.py` | Sharpe, max drawdown, win rate, trades, EV/trade. Slice-safe. |
| `strategies.py` | Candidate signals: buy&hold, random, SMA crossover, mean-reversion (z-score). |
| `walkforward.py` | Picks parameters on TRAIN only, scores on unseen TEST. Anti-curve-fitting. |
| `data.py` | Synthetic OHLCV (Ornstein-Uhlenbeck) for testing + CSV loader for real data. |
| `fetch_data.py` | Run LOCALLY to pull real SPY/QQQ via yfinance. |
| `run.py` | Wires it together and prints the comparison table. |

## Run it
```bash
python run.py                 # synthetic data — always works
# real data (on your own machine, it has internet):
pip install yfinance
python fetch_data.py SPY      # writes spy.csv
python run.py spy.csv
```

## How to read the output
- **FRICTIONLESS** row = the lie. Ignore it except to see raw signal.
- **LIQUID ETF** row = the truth for stocks. If a strategy isn't clearly positive here, it's dead.
- **CHEAP OPTION spread** row = why naive options trading is ruin: frequent trading through
  a ~300bp spread drives active strategies toward −100%.
- **OOS combined** (walk-forward) = the only number that isn't lying. But note: on the
  synthetic fixture it looks great *because mean-reversion was baked into the data*. On a
  true random walk the same strategy loses ~50%. **Trust real-data OOS only.**

## Validation done
1. Random walk (no edge) → mean-reversion LOSES even frictionless. Machine doesn't hallucinate edge. ✅
2. Edge present → machine detects it frictionless, costs erode it. ✅
3. No-lookahead is structural (shift in the engine, not the strategy). ✅

## Next steps
1. **Real data**: run `fetch_data.py` for SPY/QQQ/IWM, then `run.py spy.csv`. Expect the
   edge to mostly vanish after costs. That's the honest base rate.
2. **Kronos as a signal**: it plugs into `strategies.py` as one more function returning a
   position Series. It must clear the same OOS-net-of-costs bar as everything else. No
   finetuning until zero-shot shows edge on real data.
3. **Paper trade** survivors live against real quotes (Robinhood MCP) for a week+ before
   any real money.

## Honest expectation
Most likely outcome on real data: nothing beats buy-and-hold after costs. The win is the
machine and understanding *why*. If something genuinely survives walk-forward on real
data, THEN it's worth risking the $23.
