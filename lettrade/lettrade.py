import logging
from typing import Type

import pandas as pd

from lettrade.account import Account
from lettrade.base import BaseDataFeeds
from lettrade.brain import Brain
from lettrade.data import DataFeed, DataFeeder
from lettrade.exchange import Exchange
from lettrade.exchange.backtest import (
    BackTestAccount,
    BackTestDataFeed,
    BackTestDataFeeder,
    BackTestExchange,
    CSVBackTestDataFeed,
)
from lettrade.plot import Plotter
from lettrade.stats import Statistic
from lettrade.strategy import Strategy

logger = logging.getLogger(__name__)


class LetTrade(BaseDataFeeds):
    brain: Brain
    feeder: DataFeeder
    exchange: Exchange
    account: Account
    strategy: Strategy
    plotter: Plotter = None
    _stats: Statistic = None

    _plot_cls: Type[Plotter] = None

    def __init__(
        self,
        strategy: Type[Strategy],
        datas: DataFeed | list[DataFeed] | str | list[str] = None,
        feeder: DataFeeder = None,
        exchange: Exchange = None,
        plot: Type[Plotter] = Plotter,
        cash: float = 10_000.0,
        account: Account = None,
        # params: dict = {},
        *args,
        **kwargs,
    ) -> None:
        # Init DataFeeder
        if feeder:
            self.feeder = feeder
        else:
            if datas is None:
                raise RuntimeError("datas and feeder is None")

            self._init_datafeeder(datas=datas)

        # Money
        if account is None:
            account = BackTestAccount()
        self.account = account

        # Exchange
        if exchange is None:
            exchange = BackTestExchange()
        self.exchange = exchange

        # Strategy
        self.strategy = strategy(
            feeder=self.feeder,
            exchange=self.exchange,
            account=account,
            # params=params,
        )

        # Brain
        self.brain = Brain(
            strategy=self.strategy,
            exchange=self.exchange,
            feeder=self.feeder,
            cash=cash,
            *args,
            **kwargs,
        )

        self.exchange.init(
            brain=self.brain,
            feeder=self.feeder,
            account=self.account,
        )

        # Plot class
        self.exchange.brain = self.brain
        self._plot_cls = plot

    def _init_datafeeder(self, datas) -> None:
        # Support single and multiple data
        if not isinstance(datas, list):
            datas = [datas]

        # Check
        feeds = []
        for data in datas:
            match data:
                case DataFeed():
                    feeds.append(data)
                case pd.DataFrame():
                    feeds.append(BackTestDataFeed(data))
                case str():
                    feeds.append(CSVBackTestDataFeed(data))
                case _:
                    raise RuntimeError(f"data {data} is invalid")

        # Feeder
        self.feeder = BackTestDataFeeder(datas=feeds)

    def run(self, *args, **kwargs):
        self.brain.run(*args, **kwargs)

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
            plot_data = self.strategy.plot()
            self.plotter = self._plot_cls(
                feeder=self.feeder,
                exchange=self.exchange,
                data=plot_data,
            )

        self.plotter.plot(*args, **kwargs)
