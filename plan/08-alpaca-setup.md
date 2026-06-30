# 08 — Alpaca Setup (paper trading)

Home: [[PROJECT_PLAN]] · Decision: [[plan/01-decision-log]] (2026-06-30 phase-1 scope)

*How the three of us share one Alpaca paper account and feed it into the harness. Paper only.
No real money touches this repo — see the hard rule in `alpaca_paper.py`.*

## Which API did we sign up for?
**Trading API**, individual account (NOT Broker API). Broker API is for building a brokerage
for *other people* — that's the securities-law problem we already killed. We trade our own
(paper) money via the Trading API.

## One-time setup (Tenzing does this once, shares with J & H)
1. In the Alpaca dashboard, switch to **Paper Trading** (toggle, top of the dashboard).
2. Generate **paper API keys** (key id + secret). Copy them immediately — the secret shows once.
3. Locally: `cp .env.example .env` and paste the two keys into `.env` (gitignored — never commit).
4. Share the two key lines with Jonathan and Henry over a private channel. All three then run
   the *same* paper account, so we see one shared simulated portfolio. (Paper = zero legal risk.)

## Install
```bash
pip install -r requirements-alpaca.txt      # alpaca-py; optional, not needed by run.py
```

## What each file does
| File | Job |
|------|-----|
| `fetch_alpaca.py` | Pull split/dividend-ADJUSTED daily bars → `<ticker>.csv` in harness format. Free with the account. An alternative to `fetch_data.py` (yfinance). |
| `alpaca_paper.py` | Paper account client: `status` (equity/positions), `quote SYM` (display), `buy/sell SYM QTY` (submit a PAPER order). Hard-wired to the paper endpoint. |

## The data → research → paper loop
```
fetch_alpaca.py SPY   ->  spy.csv  ->  run.py spy.csv  ->  read OOS-net-of-costs verdict
       (data)                              (research, terminal)         (Henry logs it)
                                                  |
                              only a SURVIVOR advances to:
                                                  v
                          alpaca_paper.py  ->  paper-trade live for weeks  ->  trade journal
```
Nothing gets paper-traded until it beats buy-and-hold OOS net of costs in the harness.
Nothing goes to real money, ever, from this repo.

## Free vs paid data (the $99 question)
- Historical daily/minute bars for **backtesting** come free with the account — use them.
- The ~$99/mo subscription is only the *live real-time SIP* feed. We do NOT need it yet:
  paper-trade on the free IEX feed first. Only consider paid live data if a strategy survives.
- Intraday stays a researched *phase-2* (Kronos is stronger intraday) — backtest it on free
  historical minute bars; don't pay a live feed to find out a strategy doesn't work.
