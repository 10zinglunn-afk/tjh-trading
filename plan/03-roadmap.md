# 03 — Roadmap (Now / Next / Later)

Home: [[PROJECT_PLAN]]

*No dates — we move as fast as we can. This is about order and dependency, not calendar.
Move items up as they're done; add freely.*

## ▶️ Now
- **Tenzing:** clean `realdata/nio.csv` + `realdata/sofi.csv` (pre-IPO junk rows); remove
  throwaway `tqqq.kronos.csv` mock.
- **Tenzing:** run **Kronos for real** (local, not `--mock`) on the six tickers → log result
  in [[plan/02-verdict-log]].
- **Tenzing:** stand up the **web app skeleton** ([[webapp/SPEC]]) — equities first, model
  prediction vs actual + pay-per-trade equity curve vs SPY.
- **Jonathan:** write the first strategy thesis ([[research/_thesis-template]]).
- **Henry:** build the real **cost table** per instrument → feeds `costs.py`.

## ⏭️ Next
- Add the **options modeling layer** to the app (clearly labeled approximate; see
  [[webapp/options-modeling]]).
- Implement Jonathan's thesis as a signal; run it; verdict-log it.
- Henry: benchmark every result against SPY in the verdict log.
- Tenzing: wire Supabase to **record live option chains daily** (the only honest path to real
  options backtests later).

## 🔮 Later
- Intraday Kronos (data swap) if daily is dead.
- Paper-trade any survivor 2+ weeks before any real money.
- Finetune Kronos *only if* zero-shot shows OOS edge.
- Fordham research-club build-out ([[plan/00-vision]]).
