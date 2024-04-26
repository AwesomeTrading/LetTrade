from typing import Callable, Dict, List, Optional, Sequence, Tuple, Type, Union

import pandas as pd

from lettrade.strategy import Strategy

from ..commission import Commission
from ..data import DataFeed
from ..exchange import Exchange


class Brain:
    """Brain of lettrade"""

    def __init__(
        self,
        datas: list[DataFeed],
        exchange: Exchange,
        commission: Commission,
        cash=10_000,
        hedging=True,
        *args,
        **kwargs,
    ) -> None:
        self.datas: list[DataFeed] = datas
        self.data: DataFeed = datas[0]
        self.exchange: Exchange = exchange

        self._cash = cash
        self._commission = commission
        self._hedging = hedging

    def run(self):
        print("brain datas: \n", self.datas)

    def run_until(self, index=0, next=0):
        pass

    def shutdown(self):
        pass
