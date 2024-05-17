import logging
from typing import Type

import pandas as pd

from lettrade.account import Account
from lettrade.base import BaseDataFeeds
from lettrade.brain import Brain
from lettrade.commander import Commander
from lettrade.data import DataFeed, DataFeeder
from lettrade.exchange import Exchange
from lettrade.stats import Statistic
from lettrade.strategy import Strategy

logger = logging.getLogger(__name__)


def backtest(
    strategy: Type[Strategy],
    datas: DataFeed | list[DataFeed] | str | list[str] = None,
    feeder: DataFeeder = None,
    exchange: Exchange = None,
    commander: Commander = None,
    plot: Type["Plotter"] = None,
    cash: float = 10_000.0,
    account: Account = None,
    **kwargs,
):
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


class LetTrade(BaseDataFeeds):
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
        commander: Commander,
        account: Account,
        plot: Type["Plotter"] = None,
        # params: dict = {},
        *args,
        **kwargs,
    ) -> None:
        # DataFeeder
        if not feeder:
            raise RuntimeError("Feeder is invalid")
        self.feeder = feeder

        # DataFeeds
        datas = self._init_datafeeds(datas=datas)
        self.feeder.init(datas=datas)

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
        if self.commander:
            self.commander.start()

        self.brain.run(*args, **kwargs)

        if self.commander:
            self.commander.stop()

        # Only show stats when backtest data
        if not self.feeder.is_continous:
            self.stats.compute()
            self.stats.show()

    @property
    def stats(self) -> Statistic:
        if self._stats is None:
            self._stats = Statistic(
                feeder=self.feeder,
                exchange=self.exchange,
                strategy=self.strategy,
            )
        return self._stats

    def plot(self, *args, **kwargs):
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
