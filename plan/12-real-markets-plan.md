# 12 — From Backtest to Real Markets (the plan + who builds what)

Home: [[PROJECT_PLAN]] · Status: [[plan/09-status-where-we-are]] · Thesis: [[research/theses/001-cross-sectional-momentum]]

*Written 2026-09-13. This is the plan for everything still missing between "a backtest that
looks good" and "something we could responsibly run in a real market." Each task is assigned
to the Claude model best suited to its difficulty. **Humans own every go/no-go gate.** No
agent ever places an order, touches real money, or signs off a verdict.*

---

## Why this plan exists: the finding that changed the priority

On 2026-09-13 we ran the check the machine had been missing. The question: **does momentum
actually beat "own all 30 stocks equally"?** Until then, the "PSR 1.00" check had only asked
whether momentum makes money at all, and in 2019–2026 almost everything did.

| Check (30-stock list, 2019-08 → 2026-07, after costs) | Result |
|---|---|
| Extra return vs owning all 30 equally | +1.2%/yr |
| t-stat of that extra return | **0.34** (need ~2+ to believe it) |
| Months it beat owning all 30 | 48% |
| Random 10-stock picks that did as well or better (200 tries) | 26% |
| Same test with NVDA removed | 239% vs 246%: **it loses** |
| Old ~97-stock list (67 files still archived) | t = 1.65. Most of the gain came from PLUG, AMD and NIO; without those three, t = 0.72 |

**Conclusion:** momentum is **unproven, not dead**. It's still the best-supported idea we have.
Decades of academic research back it, and our data is only 7 years of one mostly-bull market.
Proof comes first. The trading plumbing only gets built if the proof holds.

---

## Who does what: model roster

| Model | Cost (in/out per 1M tokens) | Best at | Use it for | Don't use it for |
|---|---|---|---|---|
| **Fable 5.1** | $10 / $50 | The hardest reasoning, long careful analysis, spotting subtle mistakes | **Auditor and methodologist.** Designs the tricky tests, hunts for lookahead bugs, cherry-picking, and statistics that look good but are wrong | Routine coding or docs. Too expensive, and not needed |
| **Opus 5** | $5 / $25 | Complex engineering where correctness matters | Changes to the core engine (`xsect.py`, `diagnostics.py`), anything that touches orders, tax-lot logic | Mechanical edits |
| **Sonnet 5** | $2 / $10 | Clearly specified features, done well and fast | Scripts, tests, web-app panels, doc rewrites that need judgment | Designing statistical tests; money-safety code |
| **Haiku 4.5** | $1 / $5 | Fast, simple, low-risk tasks | Data downloaders, glossary entries, link updates, loops over existing functions | Anything where a subtle mistake would mislead us |

**Ground rules for every agent task:**
1. **Engine invariants still apply** (see `CLAUDE.md`): no-lookahead stays in the engine,
   costs are non-negotiable, and parameters are chosen on training data only.
2. **Review up.** Opus and Sonnet work on anything that produces a verdict gets a Fable audit
   at the end of its phase (tasks P1.7 and P2.7). The same model never grades its own
   homework.
3. **Done means verified.** Each task has a "done when" check the agent must actually run and
   show output for.
4. **Free by default** (see the cost policy in `CLAUDE.md`). An agent that hits a paid
   dependency stops and writes a proposal. It never signs up for anything.
5. **Paper only.** No task creates a live-money code path. `alpaca_paper.py` stays
   paper-locked, and agents never run order commands. Humans do.

**How to run a task:** tell Claude Code, for example, *"Run P1.2 from plan/12 with its
assigned model."* Claude spawns a subagent with that model (the Agent tool's `model`:
`fable` / `opus` / `sonnet` / `haiku`). Tasks marked ⇉ can run in parallel, each in its own
git worktree.

---

## Phase 0 — Make the machine honest about what it just found

| ID | Task | Done when | Model | Why this model | Depends on |
|---|---|---|---|---|---|
| P0.1 | **Add the missing gate.** In `xsect.py` robustness, test the monthly extra return over EW-universe: t-stat, a bootstrap confidence interval, % of months won, and a "remove the top contributor" test. A panel verdict needs t ≥ 2 to count as `EDGE?`. | `python3 xsect.py` prints the new block; the 30-name numbers match the table above (t ≈ 0.34); the verdict is no longer "survives" | **Opus 5** | Core engine plus statistics. Must not break invariants | — |
| P0.2 | **Audit the other gates for the same flaw.** Does `scan.py`'s deflated Sharpe measure skill *versus the benchmark*, or just "made money"? Are any other checks asking the wrong question? | A written audit in `research/audits/2026-09-gates.md` with each gate marked right/wrong and a concrete fix | **Fable 5.1** | Subtle methodology. This is exactly the class of mistake that slipped through before | — ⇉ |
| P0.3 | **Correct the record.** Add the 2026-09-13 finding to the Thesis 001 writeup; fix the "SURVIVES" wording in `plan/09`, the `CLAUDE.md` `xsect.py` row, and `webapp/lib/track_record.json` (rerun `export_track_record.py` once P0.1 lands) | No doc still calls momentum a survivor; the new numbers are quoted consistently | **Sonnet 5** | Needs judgment about tone and nuance, not new math | P0.1 |

## Phase 1 — Proof: does momentum really work, beyond one lucky stretch?

| ID | Task | Done when | Model | Why this model | Depends on |
|---|---|---|---|---|---|
| P1.1 | **Download long-history momentum data (free).** Ken French Data Library: the "10 Portfolios Formed on Momentum" and "Momentum Factor (Mom)" files, monthly, 1927→present. Write `fetch_french.py` → `research_data/french/` (gitignored). | CSVs load; row count and date range printed; spot-check 3 values against the website | **Haiku 4.5** | Mechanical download and parse | — ⇉ |
| P1.2 | **Long-history test.** Top-momentum-decile minus the market, 1927→now: t-stat overall and per decade, worst crashes (e.g. 2009), estimated after-cost version using our turnover (435%/yr) and 3/1 bps | `research/theses/001-long-history.md` with a table per decade and a plain-English verdict | **Opus 5** | Real statistics, where a careless reading would be easy | P1.1 |
| P1.3 | **Design a stock list without hindsight.** Research free historical S&P 500 membership sources (Wikipedia change tables, public GitHub datasets). Decide how to handle companies that later went bankrupt or were bought, whose prices are hard to get for free. **Check whether Fordham's library gives students free WRDS/CRSP access**: that's survivorship-free data at $0. | A design doc: chosen source, what bias remains, and whether a paid source clears the 20x bar (proposal only) | **Fable 5.1** | A judgment-heavy research design with hidden traps | — ⇉ |
| P1.4 | **Build it.** Implement P1.3: a point-in-time universe loader, plus `xsect.py` accepting "which stocks were eligible on each date" | Momentum vs EW (with P0.1's t-stat) rerun on the no-hindsight list over the longest window available | **Opus 5** | Engine change; lookahead risk if done wrong | P0.1, P1.3 |
| P1.5 | **Add MTUM as a baseline.** Fetch MTUM (iShares momentum ETF, 2013+); add it next to SPY/EW/random in `xsect.py` output | MTUM row appears with same-window return, Sharpe and max drawdown | **Sonnet 5** | Clearly specified addition to existing code | P0.1 ⇉ |
| P1.6 | **Cost-sensitivity sweep.** Rerun the canonical spec at 3, 10, 25 and 50 bps. At what cost does the edge over EW disappear? | A small table in the Thesis 001 writeup | **Haiku 4.5** | A loop over existing `run_panel`; no new math | P0.1 ⇉ |
| P1.7 | **Red-team Phase 1.** Independently re-derive the key numbers; hunt for lookahead, date misalignment, survivorship leaks, and multiple-testing (was anything picked after looking?) | `research/audits/phase1.md`: every result marked confirmed / wrong / unclear | **Fable 5.1** | Adversarial audit is Fable's highest-value use | P1.2, P1.4, P1.5, P1.6 |

### 🚦 Gate G1 — Humans decide: does momentum go forward? (Tenzing + Jonathan + Henry)
Criteria **written down now, before seeing the results**:
1. Long history (P1.2): the top decile beats the market after estimated costs with **t ≥ 2**,
   and no single decade supplies more than half the gain.
2. No-hindsight stock list (P1.4): top-10 beats EW of the same list with **t ≥ 2** on the
   longest available window.
3. MTUM (P1.5): our version isn't clearly worse than just holding MTUM after costs. If it is,
   the honest conclusion is "the existing ETF already does this; our DIY adds nothing."
4. The P1.7 audit finds no errors that change the conclusion.

**Pass all four** → Phase 2. **Fail any** → log it as KILL/ITERATE in [[plan/02-verdict-log]]
and pick Thesis 002. That's a valid, résumé-worthy result, not a failure.

## Phase 2 — Make it runnable, on paper only (only if G1 passes)

| ID | Task | Done when | Model | Why this model | Depends on |
|---|---|---|---|---|---|
| P2.1 | **Fresh data on a schedule.** A local scheduled job (or GitHub Action with cached, uncommitted data) runs `fetch_universe.py` after each trading day | Data is never more than 1 trading day old; a failure raises a visible warning | **Sonnet 5** | Standard ops scripting | G1 ⇉ |
| P2.2 | **`signal.py`: "what to hold this month."** Reuses `xsect.target_weights` (no new math) and prints target names and weights plus the data as-of date | Output matches the last row of the backtest's weights exactly | **Sonnet 5** | Thin wrapper; a test proves it matches | G1 ⇉ |
| P2.3 | **`rebalance.py`: target → paper orders.** Diffs current Alpaca **paper** positions against targets and builds **fractional, dollar-amount** orders (LLY ≈ $1,214 and GS ≈ $1,021 a share, against ~$400 per position). **Dry-run by default**; `--submit` requires the paper endpoint and refuses otherwise | Dry-run on the paper account prints a correct order list; the refusal is tested | **Opus 5** | Money-adjacent. Bugs here cost real money later | P2.2 |
| P2.4 | **Trade journal.** Every paper fill → `journal.jsonl`: expected price, fill price, actual cost in bps vs the modeled 3/1 | After a rebalance, the journal shows one row per order with a cost gap | **Sonnet 5** | Clearly specified logging | P2.3 |
| P2.5 | **Tests for P2.2–P2.4** with a mocked Alpaca client (no network) | `pytest` passes; covers empty account, partial fills, and the paper-only refusal | **Sonnet 5** | Standard test writing | P2.3, P2.4 |
| P2.6 | **Web-app panel.** Current picks, paper P&L vs what the backtest predicted, and journal cost gaps | Visible on `/engine`; checked in the browser | **Sonnet 5** | UI on existing API patterns | P2.4 ⇉ |
| P2.7 | **Safety audit of P2.3–P2.5.** Can any path hit a live endpoint, double-submit, or trade on stale data? | `research/audits/phase2.md`, all issues closed | **Fable 5.1** | High-stakes review | P2.5 |

## Phase 3 — Risk rules, decided before any money (parallel with Phase 2)

| ID | Task | Done when | Model | Why this model | Depends on |
|---|---|---|---|---|---|
| P3.1 | **Draft the risk policy.** Max account drawdown before stopping (backtest worst was −30.3%, Mar 2020 ≈ $1,200 on $4k), max % per stock and per sector, what "the strategy is broken" means in numbers, and who can restart it | `plan/13-risk-policy.md` drafted; **Jonathan owns and signs** | **Opus 5** | Careful reasoning; the human makes the final call | G1 ⇉ |
| P3.2 | **Kill switch in code.** `rebalance.py` refuses to trade when the P3.1 limits are breached and says why | A test with a simulated −35% account refuses; a normal account proceeds | **Opus 5** | Safety-critical logic | P2.3, P3.1 |
| P3.3 | **Sector-concentration report.** Share of each rebalance by sector (the July picks were 4 of 10 tech), using `fetch_universe.SECTORS` | Table per rebalance; flags any sector above the P3.1 cap | **Haiku 4.5** | Simple grouping over existing data | P2.2 ⇉ |
| P3.4 | **Don't "fix" the choppy-market weakness by curve-fitting.** Any proposed market filter goes through the full walk-forward and counts as extra trials in the deflated Sharpe | Only runs if someone proposes a filter; logged as a new thesis, not a tweak | **Fable 5.1** designs the test, **Opus 5** builds it | Classic self-deception trap | Only if proposed |

## Phase 4 — Real-world costs the backtest ignores

| ID | Task | Done when | Model | Why this model | Depends on |
|---|---|---|---|---|---|
| P4.1 | **Tax-drag model.** Replay backtest trades as FIFO tax lots and split gains into short-term (<1 yr) vs long-term. Estimate after-tax return for a taxable account vs a tax-advantaged one (e.g. a Roth IRA) under **stated assumed rates**, and flag wash sales | Table: pre-tax vs after-tax vs EW vs SPY. Rates are clearly labeled assumptions, not tax advice | **Opus 5** | Tax-lot logic is fiddly and easy to get subtly wrong | G1 ⇉ |
| P4.2 | **Real cost table from paper fills.** After ≥3 rebalances, compare journal costs with the 3/1 bps assumption; feed the real numbers back into `costs.py` as a named regime | **Henry signs** the new regime; momentum rerun with it | **Sonnet 5** | Straightforward analysis; the human owns the numbers | P2.4 + paper time |

## Phase 5 — Paper trading and the real-money decision (humans only)
- **Proposed change to a standing decision:** the old plan said "paper-trade 2+ weeks." With
  *monthly* rebalancing, 2 weeks is 0–1 rebalances, which proves nothing. **Proposal: at least
  3 monthly rebalances (~3 months)** before discussing real money. Needs a team decision →
  [[plan/01-decision-log]].
- **G2 (humans):** paper results within the backtest's expected range, real costs ≤ modeled,
  the kill switch never misfired, and the after-tax plan is chosen.
- **G3 (humans, deferred):** real money, if ever. No agent task exists for this on purpose.

---

## Order of work and parallel runs

```
P0.1 (Opus) ─┬─> P0.3 (Sonnet)
             ├─> P1.5 (Sonnet) ⇉ P1.6 (Haiku)
P0.2 (Fable) ⇉ P1.1 (Haiku) ─> P1.2 (Opus)
P1.3 (Fable) ─> P1.4 (Opus)
             all of P1 ─> P1.7 (Fable) ─> 🚦 G1 (humans)
G1 pass ─┬─> P2.1 ⇉ P2.2 ─> P2.3 (Opus) ─> P2.4 ─> P2.5 ─> P2.7 (Fable)
         ├─> P3.1 (Opus) ─> P3.2 (Opus);  P3.3 (Haiku)
         └─> P4.1 (Opus);  P4.2 after ≥3 paper rebalances
```

**First batch to run right now (parallel):** P0.1 (Opus), P0.2 (Fable), P1.1 (Haiku), P1.3 (Fable).

**Where the money goes:** Fable is used for 5 tasks, all design or audit, where one caught
mistake is worth more than the tokens. Opus handles 8 engine and safety tasks, Sonnet 9
routine builds, and Haiku 3 mechanical ones.
