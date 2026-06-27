"""Run this LOCALLY on your own machine (it has internet; the sandbox does not).
    pip install yfinance
    python fetch_data.py SPY
Saves spy.csv with columns: open,high,low,close,volume. Then:
    python run.py spy.csv
"""
import sys
import yfinance as yf

sym = sys.argv[1] if len(sys.argv) > 1 else 'SPY'
df = yf.download(sym, period='8y', interval='1d', auto_adjust=True, progress=False)
if hasattr(df.columns, 'nlevels') and df.columns.nlevels > 1:
    df.columns = df.columns.droplevel(1)            # flatten single-ticker multiindex
df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
df.columns = ['open', 'high', 'low', 'close', 'volume']
df.to_csv(f'{sym.lower()}.csv')
print(f'saved {sym.lower()}.csv  ({len(df)} rows)')
