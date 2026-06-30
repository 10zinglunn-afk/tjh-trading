"""HTTP API that runs the CANONICAL harness on demand.

The web app never re-implements strategy or cost math; it calls this. Every
response is built by export_results.build_payload -- the same code path as the
CLI export -- so the API and the offline export cannot drift.

    pip install -r requirements-api.txt
    uvicorn api_server:app --reload --port 8000

Endpoints:
    GET /api/health
    GET /api/tickers
    GET /api/run?ticker=synthetic&spread_bps=3&slippage_bps=1[&fee=0]
"""
import os
import re
import glob

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from costs import CostModel
from export_results import build, STRATEGIES

# Web input is untrusted: only a ticker-shaped token or 'synthetic' is allowed,
# so the path-based branch in resolve_data can never be reached from the web.
TICKER_RE = re.compile(r'^[A-Za-z0-9.\-]{1,12}$')

app = FastAPI(title="Skeptic's-machine harness API", version="1.0")

# CORS: the Next.js front end is a different origin. Lock this down in prod via
# ALLOWED_ORIGINS (comma-separated); default '*' is fine for local dev.
origins = os.environ.get('ALLOWED_ORIGINS', '*').split(',')
app.add_middleware(
    CORSMiddleware, allow_origins=[o.strip() for o in origins],
    allow_methods=['GET'], allow_headers=['*'])


def local_tickers():
    """Tickers we can serve from committed/cached CSVs, no network needed."""
    found = set()
    for d in ('realdata', 'data_cache'):
        for p in glob.glob(os.path.join(d, '*.csv')):
            base = os.path.basename(p)
            if base.endswith('.kronos.csv'):
                continue
            found.add(os.path.splitext(base)[0].lower())
    return sorted(found)


@app.get('/api/health')
def health():
    return {'status': 'ok'}


@app.get('/api/tickers')
def tickers():
    items = [{'id': 'synthetic', 'label': 'Synthetic (demo, edge baked in)', 'source': 'local'}]
    for t in local_tickers():
        items.append({'id': t, 'label': t.upper(), 'source': 'local'})
    return {
        'tickers': items,
        'note': 'Any other valid symbol is fetched live via yfinance on the server '
                'if available (e.g. SPY, AAPL).',
        'strategies': [{'id': k, 'label': v['label'], 'description': v['description'],
                        'tunable': v['tunable']} for k, v in STRATEGIES.items()],
    }


@app.get('/api/run')
def run(ticker: str = Query('synthetic'),
        spread_bps: float = Query(3.0, ge=0, le=10000),
        slippage_bps: float = Query(1.0, ge=0, le=10000),
        fee: float = Query(0.0, ge=0)):
    if not TICKER_RE.match(ticker):
        raise HTTPException(422, f"Invalid ticker '{ticker}'. Use a symbol like SPY or 'synthetic'.")
    spec = None if ticker.lower() == 'synthetic' else ticker
    cost = CostModel(spread_bps=spread_bps, slippage_bps=slippage_bps, fixed_fee=fee)
    try:
        result, _ = build(spec, display_cost=cost)
    except RuntimeError as e:                  # unknown ticker / yfinance missing / empty data
        raise HTTPException(400, str(e))
    return result
