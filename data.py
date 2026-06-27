"""Data layer. Real data via fetch_data.py (run locally). Synthetic generator here
so the harness runs anywhere and we can VERIFY it detects real edge when present."""
import numpy as np
import pandas as pd


def synthetic_ohlcv(n=1500, seed=7, kappa=0.0, sigma=0.012, drift=0.0,
                    level=100.0, start='2018-01-01'):
    """Ornstein-Uhlenbeck on log-price:
        log P_t = log P_{t-1} + kappa*(log level - log P_{t-1}) + drift + sigma*eps
    kappa=0  -> random walk: an efficient market with NO edge to find (sanity floor).
    kappa>0  -> price reverts to `level`: a genuine edge the z-score strategy SHOULD catch.
    This is a test fixture, NOT market data."""
    rng = np.random.default_rng(seed)
    logp = np.empty(n); logp[0] = np.log(level); theta = np.log(level)
    for t in range(1, n):
        logp[t] = logp[t-1] + kappa * (theta - logp[t-1]) + drift + rng.normal(0, sigma)
    close = pd.Series(np.exp(logp), index=pd.bdate_range(start=start, periods=n))
    high = close * (1 + np.abs(rng.normal(0, 0.003, n)))
    low  = close * (1 - np.abs(rng.normal(0, 0.003, n)))
    openp = close.shift(1).fillna(close.iloc[0])
    vol = rng.integers(1_000_000, 5_000_000, n)
    return pd.DataFrame({'open':openp,'high':high,'low':low,'close':close,'volume':vol})


def load_csv(path):
    df = pd.read_csv(path, parse_dates=[0], index_col=0)
    df.columns = [c.lower() for c in df.columns]
    return df
