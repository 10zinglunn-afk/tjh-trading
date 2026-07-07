# Glossary

*Shared vocabulary so nobody is lost in Tenzing's testing jargon, and Tenzing isn't lost in
finance jargon. Ask to add a term if you hit one that isn't here.*

## Testing / the engine
- **Out-of-sample (OOS):** tested on data the strategy was NOT tuned on. The only honest test
  — testing on the same data you tuned on is how you fool yourself into a fake edge.
- **Walk-forward:** pick your settings using only past data, test on the next chunk you
  haven't seen yet, then roll forward in time and repeat. Prevents cheating with hindsight.
- **Lookahead bias:** accidentally letting a strategy "see the future" when deciding what to
  do today. Our engine is built so this literally can't happen.
- **Curve-fitting / overfitting:** tuning a strategy until it perfectly matches past noise
  instead of a real pattern. Looks amazing on old data, falls apart going forward.
- **Net of costs:** after subtracting real trading costs (spread, slippage, fees). The only
  result that counts — a strategy that only "wins" before costs isn't a real strategy.
- **Basis points (bps):** 1 bps = 0.01% of the trade. Costs are usually quoted this way.
- **Sharpe ratio:** how much return you got per unit of bumpiness/risk. Higher = smoother ride
  for the same return. A number around 1.0 is decent; much higher on thin data is suspicious.
- **Max drawdown:** the worst peak-to-bottom loss along the way. How much pain you'd feel
  holding this strategy through its worst stretch.
- **Buy-and-hold / benchmark:** just buying the asset (usually the S&P 500, "SPY") and doing
  nothing. The bar every active strategy has to beat, or it wasn't worth the effort.
- **Equal-weight (EW):** putting the same dollar amount into every stock, instead of picking
  favorites. Used as an honest baseline — "did picking stocks actually help, or would owning
  everything equally have done just as well?"
- **Survivorship bias:** testing only on companies that are still around today naturally makes
  results look better than reality, because the failures got quietly excluded. Always ask
  "would this list have looked different 5 years ago?"
- **Deflated / probabilistic Sharpe:** a statistical haircut applied to a good-looking result
  to account for the fact that if you test enough different ideas, some will look good purely
  by chance. A high raw Sharpe after testing 300 things is less impressive than the same
  Sharpe after testing 1 thing.
- **Red flag:** an automatic warning the testing tool prints when a result looks fragile (too
  few trades, only wins in one type of market, most of the gain from one lucky year, etc.).
  A red flag isn't an automatic kill — it's a prompt for a human to look closer.
- **Regime (up / down / choppy):** what kind of market it was during a given stretch. A
  strategy that only works in trending ("up") markets and loses in choppy ones is not
  "all-weather" — that's a real limitation, not a bug.

## Options (for the modeling/learning layer — we don't trade real options money yet)
- **Call / put:** the right to buy / sell a stock at a set price by a set date.
- **Strike:** the price the option lets you transact at.
- **Expiry:** the date the option stops existing.
- **Premium:** what you pay to buy the option.
- **Implied volatility (IV):** the market's guess at how bumpy the stock will be. Higher IV =
  more expensive options.
- **Theta decay:** an option loses value just from time passing, even if the stock doesn't
  move. This is why you can correctly guess the direction and still lose money on an option —
  and why naive options trading tends to bleed out over time.
- **Bid/ask spread:** the gap between the buy price and sell price. Wide on options — a
  backtest that assumes you always get the mid-price is lying to you.
