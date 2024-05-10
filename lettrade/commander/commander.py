from abc import ABCMeta, abstractmethod

from lettrade.account import Account
from lettrade.brain import Brain
from lettrade.data import DataFeed, DataFeeder
from lettrade.exchange import Exchange
from lettrade.plot import Plotter
from lettrade.strategy import Strategy


class Commander(metaclass=ABCMeta):
    lettrade: "LetTrade"
    brain: Brain
    feeder: DataFeeder
    exchange: Exchange
    account: Account
    strategy: Strategy
    plotter: Plotter = None

    def __init__(self) -> None:
        super().__init__()

    def init(self, lettrade: "LetTrade", brain: Brain, exchange, strategy: Strategy):
        self.lettrade = lettrade
        self.brain = brain
        self.exchange = exchange
        self.strategy = strategy

    @abstractmethod
    def start(self):
        pass
