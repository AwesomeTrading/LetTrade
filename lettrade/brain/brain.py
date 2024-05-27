import logging

from lettrade.base.error import LetTradeNoMoreData
from lettrade.commander import Commander
from lettrade.data import DataFeed, DataFeeder
from lettrade.exchange import Exchange, Execute, Order, Position, Trade
from lettrade.strategy import Strategy

logger = logging.getLogger(__name__)


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
        self.data._set_main()

        self.strategy.init()

        self.feeder.start()
        self.exchange.start()

        # Load indicators
        indicators_loaders = self._indicators_loaders()
        self._indicators_load(indicators_loaders)

        self.strategy.start(*self.datas)

        while self.feeder.alive():
            # Load feeder next data
            try:
                self.feeder.next()
                self.exchange.next()

                # Realtime continous update data, then rebuild indicator data
                if self.feeder.is_continous:
                    self._indicators_load(indicators_loaders)

                self.strategy.next(*self.datas)
            except LetTradeNoMoreData:
                break
            except Exception as e:
                logger.exception("Bot running error", exc_info=e)
                break

        self.strategy.end(*self.datas)

    def _indicators_loaders(self) -> list:
        """Init indicators loaders function and args

        Returns:
            list: List of indicator loader. Ex: [_loader_function_, list[...args]]
        """
        loaders = []
        for data in self.datas:
            fn_name = f"indicators_{data.name.lower()}"
            if hasattr(self.strategy, fn_name):
                fn = getattr(self.strategy, fn_name)
            else:
                fn = self.strategy.indicators
            loaders.append([fn, [data]])
        return loaders

    def _indicators_load(self, loaders: list):
        for loader in loaders:
            fn, args = loader
            fn(*args)

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
