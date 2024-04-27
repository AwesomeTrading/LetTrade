from lettrade.strategy import Strategy

from ..commission import Commission
from ..data import DataFeed, DataFeeder
from ..exchange import Exchange
from ..strategy import Strategy


class Brain:
    """Brain of lettrade"""

    def __init__(
        self,
        strategy: Strategy,
        feeder: DataFeeder,
        commission: Commission = None,
        cash=10_000,
        hedging=True,
        *args,
        **kwargs,
    ) -> None:
        self.strategy: Strategy = strategy
        self.exchange: Exchange = strategy.exchange
        self.feeder: DataFeeder = feeder
        self.datas: list[DataFeed] = self.exchange.datas
        self.data: DataFeed = self.exchange.data

        self._cash = cash
        self._commission = commission
        self._hedging = hedging

    def run(self):
        self.strategy.init()

        self.feeder.pre_feed()
        self.strategy.indicators(self.data)

        while self.feeder.alive():
            # Load feader next data
            self.feeder.next()

            # Realtime continous update data, then rebuild indicator data
            if self.feeder.is_continous:
                self.strategy.indicators(self.data)

            self.strategy.next(self.data)

        self.strategy.end()

    def run_until(self, index=0, next=0):
        pass

    def shutdown(self):
        pass
