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
        data: DataFeed | list[DataFeed] = None,
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
            self._init_datafeeder(data=data, csv=csv)

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

    def _init_datafeeder(self, data=None, csv=None) -> None:
        # Data init
        if not data:
            if csv:
                data = CSVBackTestDataFeed(csv)

        # Support single and multiple data
        if not isinstance(data, list):
            data = [data]

        # Check
        datas = []
        for d in data:
            # Cast to DataFeed
            if not isinstance(d, DataFeed):
                datas.append(BackTestDataFeed(d))
            else:
                datas.append(d)

        # Feeder
        self.feeder = BackTestDataFeeder(datas)

    def run(self, *args, **kwargs):
        self.brain.run(*args, **kwargs)

    def plot(self, *args, **kwargs):
        if self.plotter is None:
            logger.error("plot is undefined")
            return

        self.plotter.plot(*args, **kwargs)
