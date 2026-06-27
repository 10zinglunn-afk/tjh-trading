"""Performance metrics. Equity is recomputed from net returns so this works on
any slice of a backtest (needed for walk-forward fold scoring)."""
import numpy as np


def compute_metrics(df, ppy=252):
    net = df['net'].values
    n = len(net)
    if n == 0:
        return {k: np.nan for k in
                ['total_return','cagr','sharpe','ann_vol','max_drawdown',
                 'num_trades','avg_turnover','win_rate','ev_per_trade_frac','bars']}
    eq = np.cumprod(1 + net)
    total_return = eq[-1] - 1
    years = n / ppy
    cagr = eq[-1] ** (1 / years) - 1 if years > 0 and eq[-1] > 0 else np.nan
    vol = net.std(ddof=1) * np.sqrt(ppy) if n > 1 else np.nan
    sharpe = (net.mean() * ppy) / vol if vol and vol > 0 else np.nan
    peak = np.maximum.accumulate(eq)
    max_dd = (eq / peak - 1).min()
    turn = df['turnover'].values if 'turnover' in df else np.zeros(n)
    trades = int((turn > 1e-9).sum())
    held = df['held'].abs().values if 'held' in df else np.ones(n)
    active = held > 1e-9
    win_rate = (net[active] > 0).sum() / active.sum() if active.sum() > 0 else np.nan
    ev = net.sum() / trades if trades > 0 else np.nan
    return {'total_return':total_return,'cagr':cagr,'sharpe':sharpe,'ann_vol':vol,
            'max_drawdown':max_dd,'num_trades':trades,'avg_turnover':turn.mean(),
            'win_rate':win_rate,'ev_per_trade_frac':ev,'bars':n}
