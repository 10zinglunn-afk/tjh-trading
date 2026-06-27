"""Cost model. The single most important file in the project.
A strategy is only real if it survives THIS. Costs are expressed in basis points
(bps): 1 bp = 0.01%. A 'liquid ETF' like SPY has a tiny spread (~1-3 bps);
a cheap weekly option can have a spread of hundreds of bps."""
from dataclasses import dataclass
import numpy as np


@dataclass
class CostModel:
    spread_bps: float = 3.0      # full bid-ask spread in bps
    slippage_bps: float = 1.0    # extra adverse fill beyond mid, bps
    fixed_fee: float = 0.0       # $ per trade (Robinhood equity commission = 0)
    capital: float = 10_000.0    # account size -> turns fixed_fee into a fraction

    def cost_fraction(self, turnover):
        """turnover[t] = |position[t] - position[t-1]|  (fraction of capital traded).
        Each unit of turnover crosses HALF the spread (mid->ask) plus slippage.
        fixed_fee is charged on any bar where a trade happens, as a fraction of capital
        -- this is what quietly destroys a $23 account."""
        turnover = np.asarray(turnover, dtype=float)
        prop  = turnover * (0.5 * self.spread_bps + self.slippage_bps) / 1e4
        fixed = np.where(turnover > 1e-12, self.fixed_fee / max(self.capital, 1e-9), 0.0)
        return prop + fixed
