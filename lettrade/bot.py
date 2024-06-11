import logging
import os
from typing import Any, Literal, Optional, Type

from lettrade.account import Account
from lettrade.brain import Brain
from lettrade.commander import Commander
from lettrade.data import DataFeed, DataFeeder
from lettrade.exchange import Exchange
from lettrade.plot import Plotter
from lettrade.stats import BotStatistic
from lettrade.strategy import Strategy

logger = logging.getLogger(__name__)


class LetTradeBot:

    datas: list[DataFeed]
    """DataFeed list for bot"""
    data: DataFeed
    """Main DataFeed for bot"""

    brain: Brain
    """Brain of bot"""
    feeder: DataFeeder
    """DataFeeder help to handle `datas`"""
    exchange: Exchange
    """Trading exchange and events"""
    account: Account
    """Trading account handler"""
    strategy: Strategy
    """Strategy"""
    commander: Optional[Commander] = None
    """Control the bot"""
    plotter: Optional[Plotter] = None
    """Plot graphic results"""
    stats: Optional[BotStatistic] = None

    _strategy_cls: Type[Strategy]
    _feeder_cls: Type[DataFeeder]
    _exchange_cls: Type[Exchange]
    _account_cls: Type[Account]
    _commander_cls: Optional[Type[Commander]]
    _plotter_cls: Optional[Type[Plotter]]
    _stats_cls: Optional[Type[BotStatistic]]
    _kwargs: dict[str, Any]
    _name: str

    def __init__(
        self,
        strategy: Type[Strategy],
        datas: DataFeed | list[DataFeed] | str | list[str],
        feeder: Type[DataFeeder],
        exchange: Type[Exchange],
        account: Type[Account],
        commander: Optional[Type[Commander]] = None,
        plotter: Optional[Type[Plotter]] = None,
        stats: Optional[Type[BotStatistic]] = None,
        name: Optional[str] = None,
        **kwargs,
    ) -> None:
        logger.info("New bot: %s", name)

        self._strategy_cls = strategy
        self._feeder_cls = feeder
        self._exchange_cls = exchange
        self._account_cls = account
        self._commander_cls = commander
        self._plotter_cls = plotter
        self._stats_cls = stats

        self._name = name
        self._kwargs = kwargs

        # DataFeeds
        self.datas = datas
        self.data = self.datas[0]

    def init(self):
        # Feeder
        self.feeder = self._feeder_cls(**self._kwargs.get("feeder_kwargs", {}))
        self.feeder.init(self.datas)

        # Account
        self.account = self._account_cls(**self._kwargs.get("account_kwargs", {}))

        # Exchange
        self.exchange = self._exchange_cls(**self._kwargs.get("exchange_kwargs", {}))

        # Commander
        if self._commander_cls:
            self.commander = self._commander_cls(
                **self._kwargs.get("commander_kwargs", {})
            )

        # Strategy
        self.strategy = self._strategy_cls(
            feeder=self.feeder,
            exchange=self.exchange,
            account=self.account,
            commander=self.commander,
            **self._kwargs.get("strategy_kwargs", {}),
        )

        # Brain
        self.brain = Brain(
            strategy=self.strategy,
            exchange=self.exchange,
            feeder=self.feeder,
            commander=self.commander,
            **self._kwargs.get("brain_kwargs", {}),
        )

        # Init
        if self.commander:
            self.commander.init(
                lettrade=self,
                brain=self.brain,
                exchange=self.exchange,
                strategy=self.strategy,
            )
        self.exchange.init(
            brain=self.brain,
            feeder=self.feeder,
            account=self.account,
            commander=self.commander,
        )

        # Stats
        self.stats = self._stats_cls(
            feeder=self.feeder,
            exchange=self.exchange,
            strategy=self.strategy,
            **self._kwargs.get("stats_kwargs", {}),
        )

        # Plotter
        if self._plotter_cls:
            self.plotter = self._plotter_cls(
                self,
                **self._kwargs.get("plotter_kwargs", {}),
            )

        if __debug__:
            logger.info("Bot %s inited with %d datas", self._name, len(self.datas))

    def start(self):
        if not hasattr(self, "brain"):
            self.init()

        self.brain.start()

        if __debug__:
            logger.info("Bot %s started with %d datas", self._name, len(self.datas))

    def run(self):
        if self.commander:
            self.commander.start()

        self.brain.run()

        if self.commander:
            self.commander.stop()

        if self._stats_cls:
            self.stats.compute()

    def plot(self, *args, **kwargs):
        """Plot strategy result"""
        if __debug__:
            from .utils.docs import is_docs_session

            if is_docs_session():
                return

        self.plotter.plot(*args, **kwargs)

    def stop(self):
        """Stop strategy"""
        self.brain.stop()
        if self.plotter is not None:
            self.plotter.stop()

    @classmethod
    def new_bot(
        cls,
        datas: list[DataFeed],
        strategy_cls: Type[Strategy],
        feeder_cls: Type[DataFeeder],
        exchange_cls: Type[Exchange],
        account_cls: Type[Account],
        commander_cls: Type[Commander],
        plotter_cls: Type[Plotter],
        stats_cls: Type[BotStatistic],
        name: Optional[str] = None,
        **kwargs,
    ) -> "LetTradeBot":
        bot = cls(
            strategy=strategy_cls,
            datas=datas,
            feeder=feeder_cls,
            exchange=exchange_cls,
            account=account_cls,
            commander=commander_cls,
            plotter=plotter_cls,
            stats=stats_cls,
            name=name,
            **kwargs,
        )
        return bot

    @classmethod
    def start_bot(
        cls,
        bot: Optional["LetTradeBot"] = None,
        **kwargs,
    ):
        if bot is None:
            bot = cls.new_bot(**kwargs)
        bot.init(**kwargs.get("init_kwargs", {}))
        bot.start()
        return bot

    @classmethod
    def run_bot(
        cls,
        bot: Optional["LetTradeBot"] = None,
        datas: Optional[list[DataFeed]] = None,
        id: Optional[int] = None,
        name: Optional[str] = None,
        result: Literal["str", "stats", "bot", None] = "str",
        **kwargs,
    ):
        # Set name for current processing
        if name is None:
            d = datas[0] if datas else bot.data
            name = f"{id}-{os.getpid()}-{d.name}"

        if bot is None:
            bot = cls.start_bot(
                datas=datas,
                name=name,
                **kwargs,
            )

        # bot
        bot.run(**kwargs.get("run_kwargs", {}))

        # Return type
        if result == "stats":
            return bot.stats
        if result == "str":
            return str(bot.stats)

        return bot
