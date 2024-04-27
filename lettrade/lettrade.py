import logging
from typing import Type

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

    def __init__(
        self,
        strategy: Type[Strategy],
        exchange: Exchange = None,
        datas: DataFeed | list[DataFeed] = None,
        feeder: DataFeeder = None,
        plot: Type[Plotter] = Plotter,
        csv: str = "",
        cash: float = 10_000.0,
        # params: dict = {},
        *args,
        **kwargs,
    ) -> None:
        # Init DataFeeder
        if feeder:
            self.feeder = feeder
        else:
            self._init_datafeeder(datas=datas, csv=csv)

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

        #
        # Run is done, then prepare plot
        if plot:
            self.plotter = plot(feeder=self.feeder)

    def _init_datafeeder(self, datas=None, csv=None) -> None:
        # Data init
        if not datas:
            if csv:
                datas = [CSVBackTestDataFeed(csv)]

        # Support single and multiple data
        if not isinstance(datas, list):
            datas = [datas]

        # Check
        feeds = []
        for d in datas:
            # Cast to DataFeed
            if not isinstance(d, DataFeed):
                feeds.append(BackTestDataFeed(d))
            else:
                feeds.append(d)

        # Feeder
        self.feeder = BackTestDataFeeder(datas=feeds)

    def run(self, *args, **kwargs):
        self.brain.run(*args, **kwargs)

    def plot(self, *args, **kwargs):
        if self.plotter is None:
            logger.error("plot is undefined")
            return

        self.plotter.plot(*args, **kwargs)
