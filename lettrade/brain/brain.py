from lettrade.data import DataFeed, DataFeeder
from lettrade.exchange import Exchange, Execute, Order, Position, Trade
from lettrade.strategy import Strategy


class Brain:
    """Brain of lettrade"""

    def __init__(
        self,
        strategy: Strategy,
        exchange: Exchange,
        feeder: DataFeeder,
        *args,
        **kwargs,
    ) -> None:
        self.strategy: Strategy = strategy
        self.exchange: Exchange = exchange
        self.feeder: DataFeeder = feeder
        self.datas: list[DataFeed] = self.feeder.datas
        self.data: DataFeed = self.feeder.data

    def run(self):
        self.strategy.init()

        self.feeder.pre_feed()
        self.strategy.indicators(self.data)

        while self.feeder.alive():
            # Load feeder next data
            self.feeder.next()
            self.exchange.next()

            # Realtime continous update data, then rebuild indicator data
            if self.feeder.is_continous:
                self.strategy.indicators(self.data)

            self.strategy.next(self.data)

        self.strategy.end()

    def shutdown(self):
        pass

    # Events
    def on_execute(self, execute: Execute):
        self.strategy.on_transaction(execute)
        self.strategy.on_execute(execute)

    def on_order(self, order: Order):
        self.strategy.on_transaction(order)
        self.strategy.on_order(order)

    def on_trade(self, trade: Trade):
        self.strategy.on_transaction(trade)
        self.strategy.on_trade(trade)

    def on_position(self, position: Position):
        self.strategy.on_transaction(position)
        self.strategy.on_position(position)
