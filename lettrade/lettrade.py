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


class LetTrade:
    """Help to load and connect module"""

    brain: Brain
    feeder: DataFeeder
    exchange: Exchange
    account: Account
    strategy: Strategy
    commander: Commander = None
    plotter: "Plotter" = None
    _stats: Statistic = None

    _strategy_cls: Type[Strategy]
    _feeder_cls: Type[DataFeeder]
    _exchange_cls: Type[Exchange]
    _account_cls: Type[Account]
    _commander_cls: Type[Commander]
    _plot_cls: Type["Plotter"]
    _kwargs: dict

    def __init__(
        self,
        strategy: Type[Strategy],
        datas: DataFeed | list[DataFeed] | str | list[str],
        feeder: Type[DataFeeder],
        exchange: Type[Exchange],
        account: Type[Account],
        commander: Optional[Type[Commander]] = None,
        plot: Optional[Type["Plotter"]] = None,
        **kwargs,
    ) -> None:
        self._strategy_cls = strategy
        self._feeder_cls = feeder
        self._exchange_cls = exchange
        self._account_cls = account
        self._commander_cls = commander
        self._plot_cls = plot
        self._kwargs = kwargs

        # DataFeeds
        self.datas: list[DataFeed] = self._init_datafeeds(datas)
        self.data: DataFeed = self.datas[0]

    def _init(self, is_optimize=False):
        # Feeder
        self.feeder = self._feeder_cls(**self._kwargs.get("feeder_kwargs", {}))
        # TODO: copy datas
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
            is_optimize=is_optimize,
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

    def datafeed(self, data, *args, **kwargs):
        match data:
            case DataFeed():
                return data
            case _:
                raise RuntimeError(f"data {data} is invalid")

    def _init_datafeeds(self, datas) -> None:
        # Support single and multiple data
        if not isinstance(datas, list):
            datas = [datas]

        # Check data
        feeds = [self.datafeed(data=data, index=i) for i, data in enumerate(datas)]
        return feeds

    def run(self, *args, **kwargs):
        """Run strategy"""
        self._init()

        if self.commander:
            self.commander.start()

        self.brain.run(*args, **kwargs)

        if self.commander:
            self.commander.stop()

        # Only show stats when backtest data
        if not self.feeder.is_continous:
            self.stats.compute()
            return self.stats.show()

    def stop(self):
        """Stop strategy"""
        self.brain.stop()
        if self.plotter is not None:
            self.plotter.stop()

    @property
    def stats(self) -> Statistic:
        """Get Statistic object"""
        if self._stats is None:
            self._stats = Statistic(
                feeder=self.feeder,
                exchange=self.exchange,
                strategy=self.strategy,
            )
        return self._stats

    def plot(self, *args, **kwargs):
        """Plot strategy result"""
        if __debug__:
            from .utils.docs import is_docs_session

            if is_docs_session():
                return

        if self.plotter is None:
            if self._plot_cls is None:
                raise RuntimeError("Plotter class is None")

            self.plotter = self._plot_cls(
                feeder=self.feeder,
                exchange=self.exchange,
                account=self.account,
                strategy=self.strategy,
            )

        self.plotter.plot(*args, **kwargs)
