"""Build a single self-contained HTML dashboard from the backtest harness.

Reuses the canonical harness functions (run_backtest, walk_forward, compute_metrics)
so the numbers are IDENTICAL to run.py -- this file does no strategy math of its own.

    python3 dashboard.py                 # all realdata/*.csv -> dashboard.html
    python3 dashboard.py realdata/tqqq.csv realdata/sofi.csv
    python3 dashboard.py --out my.html

Output is one HTML file with the results JSON inlined: no server, no deps to view.
Hand it to anyone, they double-click it. Leads with a ticker x strategy SURVIVAL
GRID (does it beat buy-and-hold, net of costs, out-of-sample) -- the honest view.
"""
import os
import sys
import glob
import json
import pandas as pd

from data import load_csv
from costs import CostModel
from backtest import run_backtest
from metrics import compute_metrics
from strategies import (buy_and_hold, random_strategy, sma_crossover,
                        mean_reversion, kronos_signal)
from walkforward import walk_forward

REGIMES = [
    ('frictionless', 'Frictionless (the lie)', CostModel(spread_bps=0,   slippage_bps=0)),
    ('etf',          'Liquid ETF (3/1 bps)',   CostModel(spread_bps=3,   slippage_bps=1)),
    ('option',       'Cheap option (300/50)',  CostModel(spread_bps=300, slippage_bps=50)),
]
DOWNSAMPLE = 300  # max equity-curve points per series (keeps HTML small)


def base_strats(forecast):
    s = {
        'buy_and_hold': (buy_and_hold, {}),
        'random':       (random_strategy, {'seed': 1}),
        'sma_20_100':   (sma_crossover, {'fast': 20, 'slow': 100}),
        'meanrev_20_1': (mean_reversion, {'lookback': 20, 'entry_z': 1.0}),
    }
    if forecast is not None:
        s['kronos'] = (kronos_signal, {'forecast': forecast, 'threshold': 0.0})
    return s


def load_kronos(path):
    sidecar = path.rsplit('.', 1)[0] + '.kronos.csv'
    if not os.path.exists(sidecar):
        return None, None
    fc = pd.read_csv(sidecar, parse_dates=[0], index_col=0)['pred_ret']
    return fc, sidecar


def curve(equity_series):
    """Downsample a cumulative-equity series to (date, value) pairs for plotting."""
    s = equity_series.dropna()
    n = len(s)
    if n == 0:
        return []
    step = max(1, n // DOWNSAMPLE)
    s = s.iloc[::step]
    return [[d.strftime('%Y-%m-%d'), round(float(v), 4)] for d, v in s.items()]


def analyze(path):
    df = load_csv(path)
    px = df['close'].astype(float)
    forecast, sidecar = load_kronos(path)
    strats = base_strats(forecast)

    ticker = os.path.splitext(os.path.basename(path))[0]
    rec = {
        'ticker': ticker,
        'path': path,
        'bars': int(len(px)),
        'start': px.index[0].strftime('%Y-%m-%d'),
        'end': px.index[-1].strftime('%Y-%m-%d'),
        'has_kronos': forecast is not None,
        'metrics': {},   # metrics[strategy][regime] = {...}
        'curves': {},    # curves[strategy] = ETF-regime equity curve
        'oos': {},       # oos[strategy] = {metrics, curve, params}
        'strategies': list(strats.keys()),
    }

    for name, (fn, kw) in strats.items():
        rec['metrics'][name] = {}
        for rk, _label, cm in REGIMES:
            out, m = run_backtest(px, fn(px, **kw), cm)
            rec['metrics'][name][rk] = {k: (None if v != v else v) for k, v in m.items()}
            if rk == 'etf':
                rec['curves'][name] = curve(out['equity'])

    # OOS walk-forward for the tunable strategies (the only numbers that aren't lying)
    mr_grid = [{'lookback': lb, 'entry_z': z}
               for lb in (10, 20, 40) for z in (0.5, 1.0, 1.5, 2.0)]
    mr_factory = lambda p: (lambda prices: mean_reversion(prices, **p))
    mr_comb, mr_chosen = walk_forward(px, mr_factory, mr_grid, CostModel(3, 1), n_folds=5)
    rec['oos']['meanrev_20_1'] = oos_pack(mr_comb, mr_chosen)

    if forecast is not None:
        k_grid = [{'threshold': th} for th in (0.0, 0.001, 0.003, 0.005, 0.01)]
        k_factory = lambda p: (lambda prices: kronos_signal(prices, forecast=forecast, **p))
        k_comb, k_chosen = walk_forward(px, k_factory, k_grid, CostModel(3, 1), n_folds=5)
        rec['oos']['kronos'] = oos_pack(k_comb, k_chosen)

    return rec


def oos_pack(combined, chosen):
    m = compute_metrics(combined)
    eq = (1 + combined['net']).cumprod() if len(combined) else combined.get('net', pd.Series(dtype=float))
    return {
        'metrics': {k: (None if v != v else v) for k, v in m.items()},
        'curve': curve(eq) if len(combined) else [],
        'params': [list(c.values()) if isinstance(c, dict) else c for c in chosen],
        'param_keys': list(chosen[0].keys()) if chosen and isinstance(chosen[0], dict) else [],
    }


def main():
    args = [a for a in sys.argv[1:]]
    out_path = 'dashboard.html'
    if '--out' in args:
        i = args.index('--out')
        out_path = args[i + 1]
        del args[i:i + 2]
    paths = args or sorted(glob.glob('realdata/*.csv'))
    paths = [p for p in paths if not p.endswith('.kronos.csv')]
    if not paths:
        print('No CSVs found. Pass paths or populate realdata/.')
        sys.exit(1)

    print(f'Building dashboard from {len(paths)} ticker(s)...')
    tickers = []
    for p in paths:
        print(f'  {p}')
        tickers.append(analyze(p))

    payload = {
        'generated': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M'),
        'regimes': [{'key': k, 'label': l} for k, l, _ in REGIMES],
        'tickers': tickers,
    }
    html = HTML_TEMPLATE.replace('/*DATA*/', json.dumps(payload))
    with open(out_path, 'w') as f:
        f.write(html)
    print(f'Wrote {out_path} ({os.path.getsize(out_path)//1024} KB) -- open it in any browser.')


# HTML template lives in dashboard_template.py to keep this file readable.
from dashboard_template import HTML_TEMPLATE  # noqa: E402

if __name__ == '__main__':
    main()
