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
    GET /api/universe?refresh=false        # data provenance (Engine Room)
    GET /api/engine/scan?refresh=false     # live wide scan (scan.scan_universe)
    GET /api/engine/momentum?refresh=false # live Thesis 001 (xsect pipeline)
    GET /api/alpaca/status                 # paper account (graceful if keys absent)
"""
import os
import re
import glob

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from costs import CostModel
from export_results import build, STRATEGIES
import engine_api

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


# ---- Engine Room: live universe data / wide scan / Thesis 001 / paper account ----------
# All computed in canonical Python (engine_api.py wraps scan.py / xsect.py unmodified);
# the browser only renders the JSON. First hit after a cold start or TTL expiry may be
# slow (live vendor fetch + full scan) -- the UI says so instead of hiding it.

@app.get('/api/universe')
def universe(refresh: bool = Query(False)):
    return engine_api.ensure_universe_data(force=refresh)


@app.get('/api/engine/scan')
def engine_scan(refresh: bool = Query(False)):
    payload = engine_api.run_scan(force=refresh)
    if 'error' in payload:                     # every vendor fetch failed -- honest 503
        raise HTTPException(503, payload['error'])
    return payload


@app.get('/api/engine/momentum')
def engine_momentum(refresh: bool = Query(False)):
    payload = engine_api.run_momentum(force=refresh)
    if 'error' in payload:
        raise HTTPException(503, payload['error'])
    return payload


@app.get('/api/alpaca/status')
def alpaca_status():
    return engine_api.alpaca_status()
