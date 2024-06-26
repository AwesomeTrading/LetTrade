from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from lettrade.account import Account
from lettrade.data import DataFeeder

if TYPE_CHECKING:
    # Recusive
    from lettrade import LetTradeBot
    from lettrade.brain import Brain
    from lettrade.exchange import Exchange
    from lettrade.plot import Plotter
    from lettrade.strategy import Strategy


class Commander(ABC):
    """
    Abstract class for strategy commander. Help to manage and report strategy real-time
    """

    bot: "LetTradeBot"
    brain: "Brain"
    feeder: DataFeeder
    exchange: "Exchange"
    account: Account
    strategy: "Strategy"
    plotter: "Plotter | None" = None

    _name: str

    def init(
        self,
        bot: "LetTradeBot",
        brain: "Brain",
        exchange: "Exchange",
        strategy: "Strategy",
    ):
        """Init commander dependencies

        Args:
            bot (LetTradeBot): LetTradeBot object
            brain (Brain): Brain of bot
            exchange (Exchange): Manage bot trading
            strategy (Strategy): Strategy of bot
        """
        self.bot = bot
        self.brain = brain
        self.exchange = exchange
        self.strategy = strategy

        self._name = self.bot._name

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
