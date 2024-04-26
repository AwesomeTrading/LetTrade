from typing import Type

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


class LetTrade:
    data: DataFeed
    datas: list[DataFeed]
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
        self.exchange._load(feeder=self.feeder)

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

    def _init_datafeeder(self, data=None, csv=None) -> None:
        # Data init
        if not data:
            if csv:
                data = CSVBackTestDataFeed(csv)

        # Support single and multiple data
        if not isinstance(data, list):
            data = [data]

        # Check
        self.datas = []
        for d in data:
            # Cast to DataFeed
            if not isinstance(d, DataFeed):
                self.datas.append(BackTestDataFeed(d))
            else:
                self.datas.append(d)

        # Alias
        self.feeder = BackTestDataFeeder(self.datas)

    def run(self):
        self.brain.run()

    def plot(self):
        if self.plotter is None:
            self.plotter = Plotter(self.datas)

        self.plotter.plot()
