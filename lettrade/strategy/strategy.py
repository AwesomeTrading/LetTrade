from abc import ABCMeta, abstractmethod
from typing import Optional

from lettrade.account import Account
from lettrade.data import DataFeed, DataFeeder
from lettrade.exchange import Exchange, Execute, Order, Position, Trade


class Strategy(metaclass=ABCMeta):
    def __init__(self, feeder: DataFeeder, exchange: Exchange, account: Account):
        self.__feeder: DataFeeder = feeder
        self.__exchange: Exchange = exchange
        self.__account: Account = account

    def init(self):
        pass

    def indicators(self):
        """
        All indicator and signal should implement here to cacheable
        Because of lettrade will cache/pre-load DataFeeds
        """

    @abstractmethod
    def next(self):
        pass

    def end(self):
        pass

    def plot(self):
        pass

    def buy(
        self,
        *,
        size: Optional[float] = None,
        limit: Optional[float] = None,
        stop: Optional[float] = None,
        sl: Optional[float] = None,
        tp: Optional[float] = None,
        tag: object = None,
        **kwargs,
    ):
        """
        Place a new long order. For explanation of parameters, see `Order` and its properties.
        """
        if size is None:
            size = self.__account.risk()

        return self.__exchange.new_order(
            size=size,
            limit=limit,
            stop=stop,
            sl=sl,
            tp=tp,
            tag=tag,
            **kwargs,
        )

    def sell(
        self,
        *,
        size: Optional[float] = None,
        limit: Optional[float] = None,
        stop: Optional[float] = None,
        sl: Optional[float] = None,
        tp: Optional[float] = None,
        tag: object = None,
        **kwargs,
    ):
        """
        Place a new short order. For explanation of parameters, see `Order` and its properties.
        """
        if size is None:
            size = self.__account.risk()

        return self.__exchange.new_order(
            size=-size,
            limit=limit,
            stop=stop,
            sl=sl,
            tp=tp,
            tag=tag,
            **kwargs,
        )

    @property
    def feeder(self) -> DataFeeder:
        return self.__feeder

    @property
    def exchange(self) -> Exchange:
        return self.__exchange

    @property
    def account(self) -> Account:
        return self.__account

    @property
    def data(self) -> DataFeed:
        return self.__exchange.data

    @property
    def datas(self) -> list[DataFeed]:
        return self.__exchange.datas

    @property
    def orders(self) -> dict[str, Order]:
        return self.__exchange.orders

    @property
    def history_orders(self) -> dict[str, Order]:
        return self.__exchange.history_orders

    @property
    def trades(self) -> dict[str, Trade]:
        return self.__exchange.trades

    @property
    def history_trades(self) -> dict[str, Trade]:
        return self.__exchange.history_trades

    @property
    def positions(self) -> dict[str, Position]:
        return self.__exchange.positions

    # Events
    def on_transaction(self, t):
        pass

    def on_execute(self, execute: Execute):
        pass

    def on_order(self, order: Order):
        pass

    def on_trade(self, trade: Trade):
        pass

    def on_position(self, position: Position):
        pass
