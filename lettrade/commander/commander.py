from abc import ABC, abstractmethod

from lettrade.account import Account
from lettrade.data import DataFeed, DataFeeder

# from lettrade.brain import Brain
# from lettrade.exchange import Exchange
# from lettrade.plot import Plotter
# from lettrade.strategy import Strategy


class Commander(ABC):
    """
    Abstract class for strategy commander. Help to manage and report strategy real-time
    """

    lettrade: "LetTrade"
    brain: "Brain"
    feeder: DataFeeder
    exchange: "Exchange"
    account: Account
    strategy: "Strategy"
    plotter: "Plotter" = None

    _name: str

    def __init__(self) -> None:
        super().__init__()

    def init(
        self,
        lettrade: "LetTrade",
        brain: "Brain",
        exchange: "Exchange",
        strategy: "Strategy",
    ):
        """Init commander dependencies

        Args:
            lettrade (LetTrade): LetTrade object
            brain (Brain): Brain of bot
            exchange (Exchange): Manage bot trading
            strategy (Strategy): Strategy of bot
        """
        self.lettrade = lettrade
        self.brain = brain
        self.exchange = exchange
        self.strategy = strategy

        self._name = self.lettrade._name

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def send_message(self, msg: str, **kwargs):
        pass

    @classmethod
    def multiprocess(cls, kwargs, **other_kwargs):
        pass
