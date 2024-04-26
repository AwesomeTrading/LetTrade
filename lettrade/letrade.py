from typing import Type

from .brain import Brain
from .data import CSVDataFeed, DataFeed
from .exchange import Exchange
from .exchange.backtest import BackTestExchange
from .strategy import Strategy


class LetTrade:
    data: DataFeed
    datas: list[DataFeed]
    brain: Brain
    strategy: Strategy
    exchange: Exchange

    def __init__(
        self,
        strategy: Type[Strategy],
        exchange: Exchange = None,
        data: DataFeed | list[DataFeed] = None,
        csv: str = "",
        cash: float = 10_000.0,
        params: dict = {},
        *args,
        **kwargs,
    ) -> None:
        # Init DataFeeds
        self._init_datas(data=data, csv=csv)

        # Exchange
        if exchange:
            self.exchange = exchange
        else:
            self.exchange = BackTestExchange()
        self.exchange._load(datas=self.datas)

        # Strategy
        self.strategy = strategy(
            exchange=self.exchange,
            params=params,
        )

        # Brain
        self.brain = Brain(
            strategy=self.strategy,
            cash=cash,
            *args,
            **kwargs,
        )

    def _init_datas(self, data=None, csv=None):
        # Data init
        if not data:
            if csv:
                data = CSVDataFeed(csv)

        # Support single and multiple data
        if not isinstance(data, list):
            data = [data]

        # Check
        self.datas = []
        for d in data:
            # Cast to DataFeed
            if not isinstance(d, DataFeed):
                self.datas.append(DataFeed(d))
            else:
                self.datas.append(d)

        # Alias
        self.data = self.datas[0]

    def run(self):
        self.brain.run()

    def plot(self):
        print("Plotting...")
