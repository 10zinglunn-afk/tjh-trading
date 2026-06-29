Alpha - everything a quant builds is in mind of servicing it.

Consensus view is already built out - expected value - we are trying to find the specific spots where we disagree with consensus and be right about that speculation more often than the other people in the same field. 

active management = forecasting the markets errors
	- Realize that a stocks move isn't one thing (multi-factored)
	- Regression to separate these factors (factor return, idiosyncratic return, and a quick gut check). Companys residuak (stocks are more individual than they look)

Data and signals 
- Traditional financial data + alternative data
- Value, momentum, size, quality. 
- It is worth to flag your universe (the set of names your willing to trade), draw sensible boundaries, raw signals you can't trade 
- Alpha forecast: volatility x how much predictive skill your signal has x how strong your signal is firing for that specific name. 
- Risk model: alpha tells you what to hope to make, risk models shows what you could lose with volatility. 
	- Covariance between all pairs of stocks 
		- instead of stock to stock - say every stock is a bundle of exposure to around 65 common factors - you only need the covariance among the factors (only 2k numbers).  
		- risk models on factors rather than raw stocks. 
	- Risk of portfolio is less than the weighted average of its parts because the stocks do not move all together 
	- Shared market risk will never diversify away. 
	- Specific risk vs systemic risk. 
	- Risk doesn't add across time but variance does.  Variance piles up , risk is the square root of variance - risk grows with the square root of time. 
	- monthly vol x rad 12 = annual vol
- Optimizer = maximize potential return - subtracting a penalty for the risk, cost of trading, while respecting constraints and position limits, staying sector neutral, turn over tabs, and how much leverage your allowed. 
- Target portfolio - optimizer hands a target. 

Implementing and trading
- Subtract as little value as possible (death by thousand cuts) : Commission for the broker, the bid ask spread, market impact, opportunity cost. 
- Implementation shortfall: hypothetical paper portfolio with no costs and compare it to your real one, the gap is your total cost 

Performance analysis:
- where is the skill and where was the luck. 






