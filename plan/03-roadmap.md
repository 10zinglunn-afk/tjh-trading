# 03 — Roadmap (Now / Next / Later)

Home: [[PROJECT_PLAN]]

*No dates — we move as fast as we can. This is about order and dependency, not calendar.
Move items up as they're done; add freely.*

## ▶️ Now
*Tenzing's app track is sequential — each step gates the next ([[plan/06-engineering-plan]]
Phase 0→1→2). Kronos is an independent research track that does not block the app.*

- **Tenzing (app, in order):**
  1. ✅ **Done (2026-06-29).** Pre-IPO junk trimmed structurally in `data.py` (nio −64, sofi
     −622 rows); mock Kronos quarantined to `realdata/_quarantine/`; `sanity_check.py` added
     (7/7 green); `requirements.txt` added. Phase 0 of [[plan/06-engineering-plan]].
  2. ✅ **Done (2026-06-29).** `export_results.py` writes a `results.json` from the canonical
     harness (prices, positions, trades, gross/net equity, per-regime metrics, OOS
     walk-forward, data-quality warnings). Verified to match `run.py` exactly and to be
     byte-stable. Phase 1 of [[plan/06-engineering-plan]].
  3. 🟢 **Built locally (2026-06-29), deploy pending.** Web app v1 ([[webapp/SPEC]]):
     Next.js front end + `api_server.py` (FastAPI) running the harness on demand — ticker +
     strategy pickers, price/signal chart with trade markers, net-of-cost equity vs buy-and-hold,
     live cost sliders, OOS verdict panel, cost-regime table. Type-checks + prod build pass;
     verified against the live API. Architecture in [[plan/01-decision-log]]. **Left:** deploy
     to Vercel + a Python host (`webapp/README.md` has the steps).
- **Tenzing (parallel research):** run **Kronos for real** (local, not `--mock`) on the six
  tickers → log result in [[plan/02-verdict-log]]. Research input, not a blocker for app v1.
- **Jonathan:** write the first strategy thesis ([[research/_thesis-template]]) with the
  economic reason, expected result, and sizing/risk rules.
- **Henry:** build the real **cost table** and tradable-universe rules → feeds `costs.py`
  and the web app verdict panel.

## ⏭️ Next
- Make the deployed app interview-strong: README, architecture notes, demo flow, and public-safe
  sample results.
- Implement Jonathan's first accepted thesis as a signal; run it; verdict-log it.
- Henry: benchmark every result against SPY / buy-and-hold in the verdict log.
- Add the **options modeling layer** to the app only as an approximate teaching overlay; see
  [[webapp/options-modeling]].
- Tenzing: wire Supabase to **record live option chains daily** after v1 ships; this is the
  honest path to future options backtests.

## 🔮 Later
- Intraday Kronos (data swap) if daily is dead.
- Paper-trade any survivor 2+ weeks before any real money.
- Finetune Kronos *only if* zero-shot shows OOS edge.
- Fordham research-club build-out ([[plan/00-vision]]).
