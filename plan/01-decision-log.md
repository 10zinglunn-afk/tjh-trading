# 01 — Decision Log

Home: [[PROJECT_PLAN]]

*Every meaningful or hard-to-reverse decision goes here, newest first. Format: date —
decision — why — who. This is how we remember why we did things and avoid relitigating them.
When a decision changes, add a NEW entry that supersedes the old one (don't delete history).*

---

### 2026-06-29 — Web app v1 = Next.js front end + a Python harness API (run on demand)
**Decision:** Build the visualizer as two services: a Next.js/Vercel front end and a FastAPI
backend (`api_server.py`) that runs the canonical harness on demand, so users can pick any
ticker and tweak cost assumptions live and see the result recomputed. The API reuses the exact
`export_results` code path the CLI uses, so the app and the offline numbers cannot drift.
**Why:** Chose the "fully done" architecture over a quick static bundle — live ticker choice +
cost tweaking is the whole point of the teaching tool, and the backend is real system-design
reps (Tenzing's learning goal). Trade-off acknowledged: more infra than a static site, so we
guard against scope creep (risk register) by shipping a working vertical slice first.
**Guardrails:** Python produces truth; no backtest math in JS; no order execution; vendor
price data stays out of public commits. Supersedes the implicit "static, no backend" framing.
**Who:** Tenzing (chose B over a static-only v1).

### 2026-06-27 — Options are paper-only until proven in the cheap-option cost regime
**Decision:** We may *model and visualize* options in the web app, but no real capital goes
into options until a strategy survives walk-forward OOS net of costs in the 300/50 bps
"cheap option" regime.
**Why:** Our own harness sends naive options strategies to ~−100%. Being right on direction
still loses to theta + wide spreads. Beginners + options + real money = fastest path to zero.
**Who:** Tenzing (Claude grilled it).

### 2026-06-27 — Build a visualizer web app as the current focus
**Decision:** Build a web app that overlays model predictions vs actual price and simulates
"pay-per-trade" P&L net of costs, with live quotes for display. See [[webapp/SPEC]].
**Why:** It's the portfolio centerpiece, drives Tenzing's Supabase/Vercel learning, and makes
results legible to the finance two. Options modeling here is zero-capital-risk.
**Who:** Tenzing.

### 2026-06-27 — Kill the "platform for outside money" idea; pursue a Fordham research club instead
**Decision:** No app where strangers deposit money for us to manage. Long-term ambition is a
*research/education* club at Fordham.
**Why:** Pooling/managing outsiders' money = unregistered investment vehicle / securities
law. A research club has no such exposure and is better for résumés. See [[plan/05-risk-register]].
**Who:** All three (idea originated loosely; formalized here).

### 2026-06-27 — Operate as an investment club; money separate from software
**Decision:** Three of us, own money, equal say, P&L split by contribution. Capital stays
indexed/paper-traded until a strategy clears the OOS-net-of-costs bar.
**Why:** Legal, simple, résumé-legible. Avoids funding unproven strategies.
**Who:** All three.

### 2026-06-27 — Zero-shot Kronos first; finetune only if it shows OOS edge
**Decision:** Run Kronos zero-shot on real data before investing in finetuning (Qlib,
multi-GPU).
**Why:** Don't pay the cost of finetuning until the cheap version shows a non-trivial edge.
**Who:** Tenzing (from project history).
