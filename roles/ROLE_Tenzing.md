# Role — Tenzing (Engineering / The Machine)

See [[PROJECT_PLAN]] for the shared context. This is *your* lane only.

## Your one-line mission
Own the machine that decides what's real: the backtest harness, the data, the signals, and
the dashboard the other two read. If the code lies or peeks at the future, the whole club's
work is worthless — so your bar is correctness, not cleverness.

## What you own
- The whole `.py` pipeline (`costs.py`, `backtest.py`, `walkforward.py`, `strategies.py`,
  `data.py`, `forecast_kronos.py`, `run.py`).
- Data integrity (clean real data, no lookahead, no junk rows).
- Turning Jonathan's strategy theses into actual signal functions and running them.
- The dashboard that makes results legible to non-coders.

## Deliverables (in order, no dates — just sequence)
1. **Clean the data.** Remove pre-IPO flat-padded rows from `realdata/nio.csv` and
   `realdata/sofi.csv`; delete the throwaway `tqqq.kronos.csv` mock. Don't let dirty data
   produce fake edges.
2. **Run Kronos for real.** Locally, not `--mock`, on all six tickers. Read the
   OOS-net-of-costs walk-forward row. Write the result in the verdict log even if (likely)
   it's "no edge on daily bars."
3. **Implement each strategy thesis Jonathan hands you** as a function
   `(prices, **kw) -> position Series in [-1,1]`. It must clear the same OOS-net-of-costs
   bar as everything else. No special pleading.
4. **Build the dashboard.** Read-only web app: results table, equity curves, cost regimes,
   live quotes via the Robinhood MCP *for display only*. This is your portfolio centerpiece
   and where your Supabase + Vercel learning lands.
5. **Fill the missing Obsidian notes:** [[Strategies]], [[Metrics]], [[Data]],
   [[Walkforward]] (currently unresolved wikilinks). Keeps the `.py` ↔ notes in sync.

## How your work is graded (be harsh with yourself)
- **No-lookahead stays structural.** Position at bar `t` is earned on `t+1` (`pos.shift(1)`)
  and that logic lives in the *engine*, never in a strategy. If you ever move it, you've
  broken the one invariant that makes our results trustworthy.
- **Every verdict is net of `costs.py`.** Frictionless numbers are for diagnosis only.
- **A green result you can't explain is a bug, not a win.** Suspiciously good = look for a
  leak first.

## What you're here to learn (your CLAUDE.md goals, applied)
Git/GitHub collaboration (you're the one reviewing J & H's markdown PRs), Supabase (RLS,
edge functions, migrations) and Vercel via the dashboard, MCP wiring (Robinhood data),
and system design — keeping the harness modular as strategies pile up.

## Your handoffs
- **From Jonathan:** a written thesis + sizing rules → you turn it into a signal + run it.
- **From Henry:** the real cost numbers per instrument → you plug them into `costs.py`'s
  regimes so the verdict reflects reality, not a guess.
- **To both:** the dashboard + verdict log, so non-coders can see what survived.

## The trap for you specifically
You can build anything, so you'll be tempted to add features (more signals, fancier model,
finetuning Kronos) before the simple question is answered. Don't. Finetuning Kronos
(Qlib, multi-GPU, real money) is only justified if zero-shot already shows an OOS edge.
Resist scope creep; ship the truth first.
