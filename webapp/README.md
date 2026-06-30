# The Skeptic's Machine — web app

A visual front end for the backtest harness. You pick a ticker and a strategy, then
watch it look good with no costs and fall apart once you pay real spreads and test it
out-of-sample. **Every number is computed by the canonical Python harness** — the browser
never runs a backtest. A pretty signal is not a real edge; this app exists to show that.

## Architecture

```
 Next.js (this folder)  ──HTTP──▶  api_server.py (FastAPI)  ──imports──▶  the harness
 Vercel                            any Python host                       costs/backtest/
 charts + controls                 runs a backtest on demand             walkforward/metrics
```

The same Python that the CLI export (`export_results.py`) uses is what the API calls, so the
app and the offline numbers cannot drift. The split is deliberate: **Python produces truth,
the web app displays it.**

## Run it locally

Two processes. From the repo root:

```bash
# 1) Backend — the harness as an API (http://127.0.0.1:8000)
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-api.txt
uvicorn api_server:app --reload --port 8000

# 2) Frontend — this folder (http://localhost:3000)
cd webapp
cp .env.local.example .env.local      # NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
npm install
npm run dev
```

Open http://localhost:3000. Drag the cost sliders and watch the equity curve and verdict
change live. (If `NEXT_PUBLIC_API_URL` is unset, the client defaults to `http://127.0.0.1:8000`.)

## Tickers

- `synthetic` and any CSV in `realdata/` or `data_cache/` are served with no network.
- Any other valid symbol (e.g. `SPY`, `AAPL`) is fetched live via yfinance on the backend
  if it's installed, and cached to `data_cache/`.

## Deploy

**Frontend → Vercel.** Set the project root to `webapp/`. Add an env var
`NEXT_PUBLIC_API_URL` pointing at your deployed backend. `npm run build` already passes.

**Backend → any Python host** (Render / Railway / Fly / a small VM):

```bash
pip install -r requirements-api.txt
uvicorn api_server:app --host 0.0.0.0 --port $PORT
```

Set `ALLOWED_ORIGINS` on the backend to your Vercel URL (comma-separated) to lock down CORS
in production; it defaults to `*` for local dev.

## Guardrails (do not break)

- No order execution, no money movement. Display only.
- No backtest math in JavaScript. If you need a new number, add it to the Python payload.
- Real-ticker data embeds vendor price series — keep `data_cache/` and `realdata/` out of any
  public commit (already gitignored). The synthetic demo is the public-safe one.
