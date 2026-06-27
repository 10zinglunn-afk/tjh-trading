"""Candidate signals. Each returns a position-weight Series in [-1, 1].
All use only causal (backward-looking) rolling windows, so they cannot peek
at the future. The backtest engine additionally shifts positions by one bar."""
import numpy as np
import pandas as pd


def buy_and_hold(prices, **kw):
    return pd.Series(1.0, index=prices.index)


def random_strategy(prices, seed=0, p_long=0.5, **kw):
    rng = np.random.default_rng(seed)
    return pd.Series(np.where(rng.random(len(prices)) < p_long, 1.0, 0.0),
                     index=prices.index)


def sma_crossover(prices, fast=20, slow=100, **kw):
    f = prices.rolling(fast).mean()
    s = prices.rolling(slow).mean()
    return (f > s).astype(float)                  # long when fast>slow else flat


def mean_reversion(prices, lookback=20, entry_z=1.0, **kw):
    ma = prices.rolling(lookback).mean()
    sd = prices.rolling(lookback).std()
    z = (prices - ma) / sd                         # how many std-devs from the mean
    pos = pd.Series(0.0, index=prices.index)
    pos[z < -entry_z] = 1.0                         # oversold -> long
    pos[z >  entry_z] = -1.0                        # overbought -> short
    return pos.fillna(0.0)


def kronos_signal(prices, forecast=None, threshold=0.0, **kw):
    """Turn a CACHED Kronos forecast into a position. Reads the precomputed next-bar
    return forecast (from forecast_kronos.py) -- it NEVER calls the model here, which
    keeps the backtest fast and makes the no-lookahead property auditable.

    forecast: Series of predicted next-bar returns, indexed like `prices`. Row t holds
              the forecast for t+1 made using info through t. Position[t] is decided from
              it; the engine's shift(1) earns it on t+1. Strided forecasts (NaNs between
              updates) are forward-filled, so the position simply persists until the next
              forecast -- a legitimate lower-frequency strategy, not a peek ahead.
    threshold: deadband; go long only if pred_ret > +threshold, short if < -threshold."""
    if forecast is None:
        raise ValueError(
            "kronos_signal needs forecast=<Series>. Run forecast_kronos.py first to "
            "create realdata/<ticker>.kronos.csv, then pass its pred_ret column.")
    f = forecast.reindex(prices.index).ffill()
    pos = pd.Series(0.0, index=prices.index)
    pos[f > threshold] = 1.0
    pos[f < -threshold] = -1.0
    return pos.fillna(0.0)
