from abc import ABC, abstractmethod
from typing import Optional

import pandas as pd

from lettrade.account import Account
from lettrade.data import DataFeed, DataFeeder
from lettrade.exchange import Exchange
from lettrade.strategy import Strategy


class Plotter(ABC):
    """
    Base class help to plot strategy
    """

    feeder: DataFeeder
    exchange: Exchange
    account: Account
    strategy: Strategy

    datas: list[DataFeed]

    _datas_stored: Optional[dict[str, DataFeed]] = None
    _jump_start_dt: Optional[pd.Timestamp] = None
    _jump_stop_dt: Optional[pd.Timestamp] = None

    def __init__(
        self,
        feeder: DataFeeder,
        exchange: Exchange,
        account: Account,
        strategy: Strategy,
    ) -> None:
        self.feeder = feeder
        self.exchange = exchange
        self.account = account
        self.strategy = strategy

        self.datas = self.feeder.datas

    @property
    def data(self) -> DataFeed:
        return self.datas[0]

    @data.setter
    def data(self, value: DataFeed) -> None:
        self.datas[0] = value

    @abstractmethod
    def stop(self):
        """stop plotter"""

    @abstractmethod
    def load(self):
        """Load plot config from `Strategy.plot()` and setup candlestick/equity"""

    @abstractmethod
    def plot(self, **kwargs):
        """Plot `equity`, `orders`, and `trades` then show"""

    def jump(
        self,
        since: int | str | pd.Timestamp | None = 0,
        range: int = 300,
        name: Optional[str] = None,
    ):
        if self._datas_stored is None:
            self._datas_stored = {d.name: d for d in self.datas}

        # Reset
        if since is None:
            self.datas = list(self._datas_stored.values())
            self._jump_start_dt = None
            self._jump_stop_dt = None
        else:  # Jump to range
            if isinstance(since, str):
                since = pd.to_datetime(since, utc=True)
                since = self.data.index.get_loc(since)
            elif isinstance(since, pd.Timestamp):
                since = self.data.index.get_loc(since)

            if name is None:
                name = self.data.name

            for i, data in enumerate(self._datas_stored.values()):
                if i == 0:
                    self.datas[i] = data.__class__(
                        data=data.l[since : since + range],
                        name=data.name,
                        timeframe=data.timeframe,
                    )
                    self._jump_start_dt = self.data.index[0]
                    self._jump_stop_dt = self.data.index[-1]
                else:
                    self.datas[i] = data.__class__(
                        data=data.loc[
                            (data.index >= self._jump_start_dt)
                            & (data.index <= self._jump_stop_dt)
                        ],
                        name=data.name,
                        timeframe=data.timeframe,
                    )

        self.load()
