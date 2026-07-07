# What To Do Right Now

*Check this page every week. This is the only page where "am I behind?" has an answer.
Last refreshed: 2026-07-06. The engineering side (the code, the data, the testing) is
caught up — the bottleneck right now is two open decisions from Jonathan and Henry.*

## 🟡 Jonathan — 1 open item
**Sign off on Strategy 001 (momentum).**
- The idea: buy the 10 stocks that have gone up the most over the last year, hold them a
  month, repeat. It's called "momentum."
- It's already been tested, twice now (once on ~90 stocks, once on a cleaner list of 30) and
  it beat every baseline both times — see **Strategy Ideas → 001 Cross-Sectional Momentum**.
- Your job is NOT to check the math. It's to answer: *does this make economic sense to you?
  Do you believe the reason it works, or do you think it's a fluke?* Write your honest answer
  on that page, then say whether you'd support moving it to fake-money (paper) trading.
- **You have not logged a single update yet** — this is the first thing the group needs from you.

## 🟡 Henry — 2 open items
1. **Approve (or reject/edit) the 30-stock test list.** Tenzing cut our stock list from ~97
   down to a clean 30 well-known companies (Apple, Microsoft, JPMorgan, etc. — full list on
   the **Results So Far** page) to make testing faster and easier to reason about. This is
   your call to formally bless as final, per your role — see **Roles → Henry**.
2. **Give your judgment on Strategy 001's result.** Same test as Jonathan's item above, but
   your angle is different: is this a *real* edge, or is it an illusion caused by the fact
   that we only tested stocks that happened to survive and do well? Read the "Caveats"
   section on that page before answering.
- **You have not logged a single update yet either** — same ask as Jonathan, above.

## ✅ Tenzing — engineering is caught up
- Built and tested the whole pipeline, cleaned the stock list to 30, and actually re-ran both
  test tools live on 2026-07-06 (results are real, not projected — see **Results So Far**).
- Left to do (not blocking Jonathan/Henry): get real (fake-money) trading account keys set up,
  and connect the two newer test tools to the automatic results log.

## Why this page matters
The code cannot approve a strategy. Only a human weighing "does this make sense" and "could
this be a fluke" can do that — see **Roles** for exactly why. Until Jonathan and Henry each
do their one item above, nothing advances, on purpose.
