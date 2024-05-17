from lettrade.commander import Commander
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
        commander: "Commander",
        *args,
        **kwargs,
    ) -> None:
        self.strategy: Strategy = strategy
        self.exchange: Exchange = exchange
        self.feeder: DataFeeder = feeder
        self.datas: list[DataFeed] = self.feeder.datas
        self.data: DataFeed = self.feeder.data

        self.commander: "Commander" = commander

    def run(self):
        self.strategy.init()

        self.feeder.start()
        self.exchange.start()
        self.strategy.indicators(self.data)
        self.strategy.start(self.data)

        while self.feeder.alive():
            # Load feeder next data
            self.feeder.next()
            self.exchange.next()

            # Realtime continous update data, then rebuild indicator data
            if self.feeder.is_continous:
                self.strategy.indicators(self.data)

            self.strategy.next(self.data)

        self.strategy.end(self.data)

    def stop(self):
        self.feeder.stop()
        self.exchange.stop()

    # Events
    def on_execute(self, execute: Execute):
        self.on_transaction(execute)
        self.strategy.on_execute(execute)

    def on_order(self, order: Order):
        self.on_transaction(order)
        self.strategy.on_order(order)

    def on_trade(self, trade: Trade):
        self.on_transaction(trade)
        self.strategy.on_trade(trade)

    def on_position(self, position: Position):
        self.on_transaction(position)
        self.strategy.on_position(position)

    def on_notify(self, *args, **kwargs):
        self.strategy.on_notify(*args, **kwargs)

    def on_transaction(self, transaction):
        if self.commander is not None:
            # TODO: send message to commander when new transaction
            self.commander.send_message(f"New transaction: {str(transaction)}")

        self.strategy.on_transaction(transaction)
