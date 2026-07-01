"""Fetch a curated LIQUID universe of daily bars into realdata/ for the wide scan.

Run LOCALLY (needs internet + `pip install yfinance`):
    python3 fetch_universe.py                 # the whole curated universe
    python3 fetch_universe.py AAPL MSFT       # just these (added to the universe)

Split/dividend-ADJUSTED closes (auto_adjust=True). The universe is Henry's call --
liquid US ETFs + large caps, "liquidity in, junk out" (plan/11 s1, charter). Yahoo data
is redistribution-restricted, so realdata/ is gitignored: we keep the fetch CODE, not the
data. Re-run any time to refresh; scan.py then picks up every realdata/*.csv automatically.
"""
import os
import sys
import yfinance as yf

# Broad, liquid, clean. Benchmarks first so spy.csv exists for scan.py's SPY comparison.
UNIVERSE = [
    "SPY", "QQQ", "IWM", "DIA", "VTI",                                  # index ETFs
    "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "TSLA", "AVGO",    # megacap tech
    "AMD", "NFLX", "ADBE", "CRM", "ORCL", "INTC", "CSCO", "QCOM", "TXN",
    "JPM", "BAC", "WFC", "GS", "V", "MA",                               # financials
    "UNH", "JNJ", "LLY", "PFE", "MRK", "ABBV",                          # health
    "WMT", "COST", "HD", "PG", "KO", "PEP", "MCD", "DIS", "NKE",        # consumer
    "XOM", "CVX", "CAT", "BA",                                          # energy/industrial
]


def save(sym, frame):
    """Normalise one ticker's OHLCV frame to harness format and write realdata/<sym>.csv."""
    frame = frame[["Open", "High", "Low", "Close", "Volume"]].dropna(how="all")
    frame.columns = ["open", "high", "low", "close", "volume"]
    frame.to_csv(f"realdata/{sym.lower()}.csv")
    return len(frame)


def main():
    syms = UNIVERSE + [s.upper() for s in sys.argv[1:] if s.upper() not in UNIVERSE]
    os.makedirs("realdata", exist_ok=True)
    # One batched, threaded request is gentler on Yahoo's rate limit than N sequential ones.
    data = yf.download(syms, period="8y", interval="1d", auto_adjust=True,
                       group_by="ticker", progress=False, threads=True)
    ok = fail = 0
    for s in syms:
        try:
            frame = data[s] if len(syms) > 1 else data
            n = save(s, frame)
            print(f"  ok   {s:6s} {n:5d} rows")
            ok += 1
        except Exception as e:                     # missing ticker / empty frame
            print(f"  FAIL {s:6s} {e}")
            fail += 1
    print(f"\n{ok} saved, {fail} failed -> realdata/  (gitignored; run scan.py next)")


if __name__ == "__main__":
    main()
