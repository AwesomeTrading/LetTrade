import logging
from typing import Type

import pandas as pd

from .base import BaseDataFeeds
from .brain import Brain
from .data import DataFeed, DataFeeder
from .exchange import Exchange
from .exchange.backtest import (
    BackTestDataFeed,
    BackTestDataFeeder,
    BackTestExchange,
    CSVBackTestDataFeed,
)
from .plot import Plotter
from .strategy import Strategy

logger = logging.getLogger(__name__)


class LetTrade(BaseDataFeeds):
    brain: Brain
    strategy: Strategy
    exchange: Exchange
    feeder: DataFeeder

    plotter: Plotter = None

    _plot_cls: Type[Plotter] = None

    def __init__(
        self,
        strategy: Type[Strategy],
        datas: DataFeed | list[DataFeed] | str | list[str] = None,
        feeder: DataFeeder = None,
        exchange: Exchange = None,
        plot: Type[Plotter] = Plotter,
        cash: float = 10_000.0,
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

        # Exchange
        if exchange:
            self.exchange = exchange
        else:
            self.exchange = BackTestExchange()
        self.exchange.feeder = self.feeder

        # Strategy
        self.strategy = strategy(
            exchange=self.exchange,
            # params=params,
        )

        # Brain
        self.brain = Brain(
            strategy=self.strategy,
            feeder=self.feeder,
            cash=cash,
            *args,
            **kwargs,
        )

        # Plot class
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

    def plot(self, *args, **kwargs):
        if self.plotter is None:
            plot_data = self.strategy.plot()
            self.plotter = self._plot_cls(feeder=self.feeder, data=plot_data)

        self.plotter.plot(*args, **kwargs)
