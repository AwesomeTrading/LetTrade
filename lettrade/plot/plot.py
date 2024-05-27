from abc import ABC, abstractmethod

from lettrade.account import Account
from lettrade.data import DataFeed, DataFeeder
from lettrade.exchange import Exchange
from lettrade.strategy import Strategy


class Plotter(ABC):
    """
    Base class help to plot strategy
    """

    _datas_stored: dict = {}

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
        self.data: DataFeed = self.feeder.data

    @abstractmethod
    def stop(self):
        """stop plotter"""

    @abstractmethod
    def load(self):
        """Load plot config from `Strategy.plot()` and setup candlestick/equity"""

    @abstractmethod
    def plot(self, **kwargs):
        """Plot `equity`, `orders`, and `trades` then show"""

    def jump(self, index, range=300, data: DataFeed = None):
        if data is None:
            data = self.data

        name = data.meta["name"]

        stored_data: DataFeed = self._datas_stored.setdefault(name, data)
        self.data = DataFeed(name=name, data=stored_data[index : index + range])

        self.load()
