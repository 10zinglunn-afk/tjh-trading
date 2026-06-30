"""Alpaca PAPER-trading client. The thin, safe bridge between a surviving strategy and a
simulated live account. Run LOCALLY with your PAPER keys.

HARD RULE (mirrors plan/01-decision-log): this module refuses to talk to anything but the
PAPER endpoint. There is no live-money code path here on purpose. Moving real money is a
human decision made by hand in the Alpaca UI, never by this repo.

    pip install -r requirements-alpaca.txt
    export APCA_API_KEY_ID=...        # PAPER key id
    export APCA_API_SECRET_KEY=...    # PAPER secret
    python alpaca_paper.py status                 # account summary
    python alpaca_paper.py quote SPY              # latest quote (display)
    python alpaca_paper.py buy SPY 1              # submit a PAPER market order, 1 share
"""
import os
import sys

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestQuoteRequest


def _keys():
    key, secret = os.getenv("APCA_API_KEY_ID"), os.getenv("APCA_API_SECRET_KEY")
    if not key or not secret:
        sys.exit("Set APCA_API_KEY_ID and APCA_API_SECRET_KEY (PAPER keys) first.")
    return key, secret


def _client():
    key, secret = _keys()
    c = TradingClient(key, secret, paper=True)          # paper=True is non-negotiable here
    return c


def status():
    a = _client().get_account()
    print(f"account     : {a.account_number}  (status={a.status})")
    print(f"equity      : ${float(a.equity):,.2f}")
    print(f"cash        : ${float(a.cash):,.2f}")
    print(f"buying_power: ${float(a.buying_power):,.2f}")
    pos = _client().get_all_positions()
    print(f"positions   : {len(pos)}")
    for p in pos:
        print(f"   {p.symbol:6s} qty={p.qty} avg={float(p.avg_entry_price):.2f} "
              f"mv=${float(p.market_value):,.2f} uPnL=${float(p.unrealized_pl):,.2f}")


def quote(sym):
    key, secret = _keys()
    data = StockHistoricalDataClient(key, secret)
    q = data.get_stock_latest_quote(StockLatestQuoteRequest(symbol_or_symbols=sym.upper()))
    q = q[sym.upper()]
    print(f"{sym.upper()}  bid={q.bid_price} x{q.bid_size}   ask={q.ask_price} x{q.ask_size}")
    print("(display only -- not a recommendation)")


def order(sym, qty, side):
    """Submit a PAPER market order. side in {'buy','sell'}."""
    req = MarketOrderRequest(
        symbol=sym.upper(),
        qty=float(qty),
        side=OrderSide.BUY if side == "buy" else OrderSide.SELL,
        time_in_force=TimeInForce.DAY,
    )
    o = _client().submit_order(req)
    print(f"PAPER {side} {qty} {sym.upper()} -> order {o.id} (status={o.status})")


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    if cmd == "status":
        status()
    elif cmd == "quote":
        quote(sys.argv[2])
    elif cmd in ("buy", "sell"):
        order(sys.argv[2], sys.argv[3], cmd)
    else:
        sys.exit("usage: status | quote SYM | buy SYM QTY | sell SYM QTY")


if __name__ == "__main__":
    main()
