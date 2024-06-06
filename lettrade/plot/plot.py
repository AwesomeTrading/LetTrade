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

    _datas_stored: dict = None
    _jump_start_dt: pd.Timestamp = None
    _jump_stop_dt: pd.Timestamp = None

    def __init__(
        self,
        feeder: DataFeeder,
        exchange: Exchange,
        account: Account,
        strategy: Strategy,
    ) -> None:
        self.feeder: DataFeeder = feeder
        self.exchange: Exchange = exchange
        self.account: Account = account
        self.strategy: Strategy = strategy

        self.datas: list[DataFeed] = self.feeder.datas

    @property
    def data(self) -> DataFeed:
        return self.datas[0]

    @data.setter
    def data(self, value: DataFeed) -> DataFeed:
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
        since: Optional[int | str | pd.Timestamp | None] = 0,
        range=300,
        name: str = None,
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
                print("since", since)

            if name is None:
                name = self.data.name

            for i, data in enumerate(self._datas_stored.values()):
                if i == 0:
                    self.datas[i] = data.__class__(
                        name=data.name,
                        data=data.l[since : since + range],
                    )
                    self._jump_start_dt = self.data.index[0]
                    self._jump_stop_dt = self.data.index[-1]
                else:
                    self.datas[i] = data.__class__(
                        name=data.name,
                        data=data.__class__(
                            name=data.name,
                            data=data.loc[
                                (data.index >= self._jump_start_dt)
                                & (data.index <= self._jump_stop_dt)
                            ],
                        ),
                    )

        self.load()
