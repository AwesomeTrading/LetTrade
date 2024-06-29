import logging
import os
from typing import Any, Literal

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
    """Bot object helps to manage actions of bot"""

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
    commander: Commander | None = None
    """Control the bot"""
    plotter: Plotter | None = None
    """Plot graphic results"""
    stats: BotStatistic | None = None

    _strategy_cls: type[Strategy]
    _feeder_cls: type[DataFeeder]
    _exchange_cls: type[Exchange]
    _account_cls: type[Account]
    _commander_cls: type[Commander] | None
    _plotter_cls: type[Plotter] | None
    _stats_cls: type[BotStatistic] | None
    _kwargs: dict[str, Any]
    _name: str | None

    def __init__(
        self,
        datas: DataFeed | list[DataFeed] | list[str] | str,
        strategy: type[Strategy],
        feeder: type[DataFeeder],
        exchange: type[Exchange],
        account: type[Account],
        commander: type[Commander] | None = None,
        plotter: type[Plotter] | None = None,
        stats: type[BotStatistic] | None = None,
        name: str | None = None,
        **kwargs,
    ) -> None:
        """_summary_

        Args:
            datas (DataFeed | list[DataFeed] | list[str] | str): _description_
            strategy (type[Strategy]): _description_
            feeder (type[DataFeeder]): _description_
            exchange (type[Exchange]): _description_
            account (type[Account]): _description_
            commander (type[Commander] | None, optional): _description_. Defaults to None.
            plotter (type[Plotter] | None, optional): _description_. Defaults to None.
            stats (type[BotStatistic] | None, optional): _description_. Defaults to None.
            name (str | None, optional): _description_. Defaults to None.
        """
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
        """Init objects from classes"""
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
                bot=self,
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
            logger.debug("Bot %s inited with %d datas", self._name, len(self.datas))

    def start(self):
        """Start bot"""
        if not hasattr(self, "brain"):
            self.init()

        self.brain.start()

        if __debug__:
            logger.debug("Bot %s started with %d datas", self._name, len(self.datas))

    def run(self):
        """Run bot"""
        if self.commander:
            self.commander.start()

        self.brain.run()

        if self.commander:
            self.commander.stop()

        if self._stats_cls:
            self.stats.compute()

    def plot(self, *args, **kwargs):
        """Plot bot result"""
        if __debug__:
            from .utils.docs import is_docs_session

            if is_docs_session():
                return

        self.plotter.plot(*args, **kwargs)

    def stop(self):
        """Stop bot"""
        self.brain.stop()
        if self.plotter is not None:
            self.plotter.stop()

    @classmethod
    def new_bot(
        cls,
        datas: list[DataFeed],
        strategy_cls: type[Strategy],
        feeder_cls: type[DataFeeder],
        exchange_cls: type[Exchange],
        account_cls: type[Account],
        commander_cls: type[Commander],
        plotter_cls: type[Plotter],
        stats_cls: type[BotStatistic],
        name: str | None = None,
        **kwargs,
    ) -> "LetTradeBot":
        """Create new bot object

        Args:
            datas (list[DataFeed]): _description_
            strategy_cls (type[Strategy]): _description_
            feeder_cls (type[DataFeeder]): _description_
            exchange_cls (type[Exchange]): _description_
            account_cls (type[Account]): _description_
            commander_cls (type[Commander]): _description_
            plotter_cls (type[Plotter]): _description_
            stats_cls (type[BotStatistic]): _description_
            name (str | None, optional): _description_. Defaults to None.

        Returns:
            LetTradeBot: _description_
        """
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
        bot: "LetTradeBot | None" = None,
        **kwargs,
    ) -> "LetTradeBot":
        """Init and start bot object

        Args:
            bot (LetTradeBot | None, optional): _description_. Defaults to None.

        Returns:
            LetTradeBot: _description_
        """
        if bot is None:
            bot = cls.new_bot(**kwargs)
        bot.init(**kwargs.get("init_kwargs", {}))
        bot.start()
        return bot

    @classmethod
    def run_bot(
        cls,
        bot: "LetTradeBot | None" = None,
        datas: list[DataFeed] | None = None,
        id: int | None = None,
        name: str | None = None,
        result: Literal["str", "stats", "bot", None] = "str",
        **kwargs,
    ) -> "LetTradeBot | BotStatistic | str | None":
        """Run bot object

        Args:
            bot (LetTradeBot | None, optional): _description_. Defaults to None.
            datas (list[DataFeed] | None, optional): _description_. Defaults to None.
            id (int | None, optional): _description_. Defaults to None.
            name (str | None, optional): _description_. Defaults to None.
            result (Literal["str", "stats", "bot", None], optional): _description_. Defaults to "str".

        Returns:
            LetTradeBot | BotStatistic | str | None: Return value will be pickle across multiprocessing.
                The cost higher from `str`, `stats` object, `bot` object
        """
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
