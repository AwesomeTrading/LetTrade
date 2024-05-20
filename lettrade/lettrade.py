import logging
from typing import Optional, Type

import pandas as pd

from lettrade.account import Account
from lettrade.brain import Brain
from lettrade.commander import Commander
from lettrade.data import DataFeed, DataFeeder
from lettrade.exchange import Exchange
from lettrade.stats import Statistic
from lettrade.strategy import Strategy

logger = logging.getLogger(__name__)


def let_backtest(
    strategy: Type[Strategy],
    datas: Optional[DataFeed | list[DataFeed] | str | list[str]],
    feeder: Optional[DataFeeder] = None,
    exchange: Optional[Exchange] = None,
    commander: Optional[Commander] = None,
    plot: Optional[Type["Plotter"]] = None,
    cash: Optional[float] = 10_000.0,
    account: Optional[Account] = None,
    **kwargs,
) -> "LetTrade":
    """
    Complete `lettrade` backtest depenencies

    Arguments:
        strategy: The Strategy implement class.

    Returns:
        The LetTrade backtest object.
    """
    from lettrade.exchange.backtest import (
        BackTestAccount,
        BackTestCommander,
        BackTestDataFeed,
        BackTestDataFeeder,
        BackTestExchange,
        CSVBackTestDataFeed,
    )
    from lettrade.plot import Plotter

    # Data
    feeds = []
    # Support single and multiple data
    if not isinstance(datas, list):
        datas = [datas]
    for data in datas:
        if isinstance(data, str):
            feeds.append(CSVBackTestDataFeed(data))
            continue

        if isinstance(data, pd.DataFrame) and not isinstance(data, DataFeed):
            feeds.append(BackTestDataFeed(data))
            continue

        if not isinstance(data, DataFeed):
            raise RuntimeError(f"Data {data} type is invalid")

    # DataFeeder
    if not feeder:
        feeder = BackTestDataFeeder()

    # Account
    if account is None:
        account = BackTestAccount()

    # Exchange
    if exchange is None:
        exchange = BackTestExchange()

    # Commander
    if commander is None:
        commander = BackTestCommander()

    # Plot
    if plot is None:
        plot = Plotter

    return LetTrade(
        strategy=strategy,
        datas=feeds,
        feeder=feeder,
        exchange=exchange,
        commander=commander,
        plot=plot,
        cash=cash,
        account=account,
        **kwargs,
    )


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

    _plot_cls: Type["Plotter"] = None

    def __init__(
        self,
        strategy: Type[Strategy],
        datas: DataFeed | list[DataFeed] | str | list[str],
        feeder: DataFeeder,
        exchange: Exchange,
        account: Account,
        commander: Optional[Commander] = None,
        plot: Optional[Type["Plotter"]] = None,
        *args,
        **kwargs,
    ) -> None:
        # DataFeeder
        if not feeder:
            raise RuntimeError("Feeder is invalid")
        self.feeder = feeder

        # DataFeeds
        self.datas: list[DataFeed] = self._init_datafeeds(datas)
        self.data: DataFeed = self.datas[0]
        self.feeder.init(self.datas)

        # Account
        if account is None:
            raise RuntimeError("Account is invalid")
        self.account = account

        # Exchange
        if exchange is None:
            raise RuntimeError("Exchange is invalid")
        self.exchange = exchange

        # Strategy
        self.strategy = strategy(
            feeder=self.feeder,
            exchange=self.exchange,
            account=self.account,
            commander=commander,
            # params=params,
        )

        # Brain
        self.brain = Brain(
            strategy=self.strategy,
            exchange=self.exchange,
            feeder=self.feeder,
            commander=commander,
            *args,
            **kwargs,
        )

        self.exchange.init(
            brain=self.brain,
            feeder=self.feeder,
            account=self.account,
            commander=commander,
        )

        # Commander
        if commander:
            self.commander = commander
            self.commander.init(
                lettrade=self,
                brain=self.brain,
                exchange=self.exchange,
                strategy=self.strategy,
            )

        # Plot class
        if plot:
            self._plot_cls = plot

    def _init_datafeeds(self, datas) -> None:
        # Support single and multiple data
        if not isinstance(datas, list):
            datas = [datas]

        # Check data
        feeds = []
        for data in datas:
            match data:
                case DataFeed():
                    feeds.append(data)
                case _:
                    raise RuntimeError(f"data {data} is invalid")

        # Feeder
        return feeds

    def run(self, *args, **kwargs):
        """Run strategy"""
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
