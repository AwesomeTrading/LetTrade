from lettrade.commander import Commander
from lettrade.data import DataFeed, DataFeeder
from lettrade.exchange import Exchange, Execute, Order, Position, Trade
from lettrade.strategy import Strategy


class Brain:
    """Brain of bot"""

    strategy: Strategy
    exchange: Exchange
    feeder: DataFeeder
    commander: Commander

    datas: list[DataFeed]
    data: DataFeed

    def __init__(
        self,
        strategy: Strategy,
        exchange: Exchange,
        feeder: DataFeeder,
        commander: Commander,
        *args,
        **kwargs,
    ) -> None:
        """_summary_

        Args:
            strategy (Strategy): _description_
            exchange (Exchange): _description_
            feeder (DataFeeder): _description_
            commander (Commander): _description_
        """
        self.strategy = strategy
        self.exchange = exchange
        self.feeder = feeder
        self.commander = commander

        self.datas = self.feeder.datas
        self.data = self.feeder.data

    def run(self):
        """Run the trading bot"""
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
        """Stop the trading bot"""
        self.feeder.stop()
        self.exchange.stop()

    # Events
    def on_execute(self, execute: Execute):
        """Receive new `Execution` event and send to `Strategy`"""
        self.on_transaction(execute)
        self.strategy.on_execute(execute)

    def on_order(self, order: Order):
        """Receive new `Order` event and send to `Strategy`"""
        self.on_transaction(order)
        self.strategy.on_order(order)

    def on_trade(self, trade: Trade):
        """Receive new `Trade` event and send to `Strategy`"""
        self.on_transaction(trade)
        self.strategy.on_trade(trade)

    def on_position(self, position: Position):
        """Receive new `Position` event and send to `Strategy`"""
        self.on_transaction(position)
        self.strategy.on_position(position)

    def on_notify(self, *args, **kwargs):
        """Receive new notify and send to Strategy"""
        self.strategy.on_notify(*args, **kwargs)

    def on_transaction(self, transaction):
        """Receive new transaction event and send to `Strategy`"""
        if self.commander is not None:
            # TODO: send message to commander when new transaction
            self.commander.send_message(f"New transaction: {str(transaction)}")

        self.strategy.on_transaction(transaction)
