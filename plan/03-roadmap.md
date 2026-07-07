# 03 — Roadmap (Now / Next / Later)

Home: [[PROJECT_PLAN]] · Status: [[plan/09-status-where-we-are]] (the up-to-date pipeline tracker)

*No dates — we move as fast as we can. This is about order and dependency, not calendar.
Move items up as they're done; add freely. Last refreshed 2026-07-06 against [[plan/09-status-where-we-are]]
and [[plan/01-decision-log]] — the machine track (web app, wide scan, Thesis 001 engine) is
DONE; what's actually "Now" is the human sign-offs, not more code.*

## ▶️ Now
*The engineering track (web app v1, wide scan, cross-sectional panel engine) is built, run,
and deployed. The bottleneck has moved from code to people — see [[plan/09-status-where-we-are]]
"the one thing blocking everything."*

- **Jonathan:** SIGN Thesis 001 (`research/theses/001-cross-sectional-momentum.md`) — it's
  pre-filled with the run and a surviving verdict attached; own or amend the economic story,
  then pre-register whether you'd advance it to paper. **Not yet done — first log entry
  still outstanding** ([[roles/log-Jonathan]]).
- **Henry:** (1) build the real cost table (bps per instrument, from actual Alpaca/market
  numbers) and ratify the **slimmed 30-name universe** (`fetch_universe.py`, cut from ~97 on
  2026-07-06 — quality over quantity; old list archived, not gone, in `realdata_archive_97/`)
  — `costs.py`'s 3/1 and 300/50 bps regimes are still Tenzing's placeholders, not Henry's
  numbers yet; (2) render a judgment (real vs. survivorship-inflated) on Thesis 001's verdict,
  now checked on **two** universes (see [[plan/02-verdict-log]] 2026-07-06). **Not yet done —
  first log entry still outstanding** ([[roles/log-Henry]]).
- **Tenzing:** (1) generate real Alpaca paper API keys and fill `.env` (currently blank —
  literally blocks stage 7 even after sign-off); (2) wire `scan.py`/`xsect.py` results into
  `verdict_log.py`'s auto-logger (`verdicts.jsonl` currently only has 2 rows from `run.py`,
  missing the wide-scan-v3 and Thesis-001 runs that are the actual research record);
  (3) add the panel-⑤ robustness/red-flag view (`diagnostics.py` output) to the per-ticker
  web app view (`webapp/app/page.tsx`) — currently only shown for Thesis 001 in the static
  track record, not for an arbitrary ticker/strategy run.

## ⏭️ Next
- Once Jonathan + Henry sign off: paper-trade Thesis 001 via `alpaca_paper.py` for 2+ weeks;
  keep a trade journal (thesis, entry, exit, expected vs actual cost).
- Make the deployed app interview-strong: README, architecture notes, demo flow.
- Add the **options modeling layer** to the app only as an approximate teaching overlay; see
  [[webapp/options-modeling]].
- Fill the missing Obsidian notes ([[Strategies]], [[Metrics]], [[Data]], [[Walkforward]] —
  still unresolved wikilinks).

## 🔮 Later
- Intraday Kronos (data swap) — parked; revisit only if we deliberately go intraday.
- Wire Supabase to **record live option chains daily** — the honest path to future options
  backtests.
- Finetune Kronos *only if* zero-shot shows OOS edge (still not run for real — parked per
  [[plan/01-decision-log]] 2026-07-02, daily-bar timeframe mismatch).
- Fordham research-club build-out ([[plan/00-vision]]).
