import logging
from typing import Optional, Type

from lettrade.account import Account
from lettrade.brain import Brain
from lettrade.commander import Commander
from lettrade.data import DataFeed, DataFeeder
from lettrade.exchange import Exchange
from lettrade.stats import Statistic
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
    commander: Commander = None
    """Control the bot"""
    plotter: "Plotter" = None
    """Plot graphic results"""
    stats: Statistic = None

    _strategy_cls: Type[Strategy]
    _feeder_cls: Type[DataFeeder]
    _exchange_cls: Type[Exchange]
    _account_cls: Type[Account]
    _commander_cls: Type[Commander]
    _plotter_cls: Type["Plotter"]
    _stats_cls: Type["Statistic"]
    _kwargs: dict
    _name: str
    _is_multiprocess: Optional[str]

    def __init__(
        self,
        strategy: Type[Strategy],
        datas: DataFeed | list[DataFeed] | str | list[str],
        feeder: Type[DataFeeder],
        exchange: Type[Exchange],
        account: Type[Account],
        commander: Optional[Type[Commander]] = None,
        plotter: Optional[Type["Plotter"]] = None,
        stats: Optional[Type["Statistic"]] = None,
        name: Optional[str] = None,
        **kwargs,
    ) -> None:
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

        self._is_multiprocess = None

    def _init(self):
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

    def run(
        self,
        multiprocess: Optional[str] = None,
        **kwargs,
    ):
        self._multiprocess(multiprocess)

        # Init objects
        self._init(**kwargs)

        if self.commander:
            self.commander.start()

        self.brain.run()

        if self.commander:
            self.commander.stop()

        if self._stats_cls:
            self.stats.compute()

    def _multiprocess(self, process, **kwargs):
        if process is not None:
            self._is_multiprocess = process

    def plot(self, *args, **kwargs):
        """Plot strategy result"""

        # if main process of multiprocessing
        if self._is_multiprocess == "main":
            logger.warning("Plot in multiprocessing is not implement yet")
            return

        if __debug__:
            from .utils.docs import is_docs_session

            if is_docs_session():
                return

        if self.plotter is None:
            if self._plotter_cls is None:
                raise RuntimeError("Plotter class is None")

            self.plotter = self._plotter_cls(
                feeder=self.feeder,
                exchange=self.exchange,
                account=self.account,
                strategy=self.strategy,
                **self._kwargs.get("plotter_kwargs", {}),
            )

        self.plotter.plot(*args, **kwargs)

    def stop(self):
        """Stop strategy"""
        self.brain.stop()
        if self.plotter is not None:
            self.plotter.stop()
