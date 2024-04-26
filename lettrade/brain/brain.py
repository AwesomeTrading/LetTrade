from typing import Callable, Dict, List, Optional, Sequence, Tuple, Type, Union

import pandas as pd

from lettrade.strategy import Strategy

from ..commission import Commission
from ..data import DataFeed
from ..exchange import Exchange
from ..strategy import Strategy


class Brain:
    """Brain of lettrade"""

    def __init__(
        self,
        strategy: Strategy,
        commission: Commission,
        cash=10_000,
        hedging=True,
        *args,
        **kwargs,
    ) -> None:
        self.strategy: Strategy = strategy
        self.exchange: Exchange = strategy.exchange
        self.datas: list[DataFeed] = self.exchange.datas
        self.data: DataFeed = self.exchange.data

        self._cash = cash
        self._commission = commission
        self._hedging = hedging

    def run(self):
        self.strategy.init()

    def run_until(self, index=0, next=0):
        pass

    def shutdown(self):
        pass
