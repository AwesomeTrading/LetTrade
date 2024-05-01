from abc import ABCMeta, abstractmethod
from typing import Optional, Tuple

import pandas as pd

from ..data import DataFeed
from ..exchange import Exchange, Execute, FastSet, Order, Position, Trade


class Strategy(metaclass=ABCMeta):
    def __init__(self, exchange):
        self._exchange: Exchange = exchange

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
        size: float,
        limit: Optional[float] = None,
        stop: Optional[float] = None,
        sl: Optional[float] = None,
        tp: Optional[float] = None,
        tag: object = None,
        **kwargs,
    ):
        """
        Place a new long order. For explanation of parameters, see `Order` and its properties.

        See `Position.close()` and `Trade.close()` for closing existing positions.

        See also `Strategy.sell()`.
        """
        assert (
            0 < size < 1 or round(size) == size
        ), "size must be a positive fraction of equity, or a positive whole number of units"
        return self._exchange.new_order(
            size,
            limit,
            stop,
            sl,
            tp,
            tag,
            **kwargs,
        )

    def sell(
        self,
        *,
        size: float,
        limit: Optional[float] = None,
        stop: Optional[float] = None,
        sl: Optional[float] = None,
        tp: Optional[float] = None,
        tag: object = None,
        **kwargs,
    ):
        """
        Place a new short order. For explanation of parameters, see `Order` and its properties.

        See also `Strategy.buy()`.

        .. note::
            If you merely want to close an existing long position,
            use `Position.close()` or `Trade.close()`.
        """
        assert (
            0 < size < 1 or round(size) == size
        ), "size must be a positive fraction of equity, or a positive whole number of units"
        return self._exchange.new_order(
            -size,
            limit,
            stop,
            sl,
            tp,
            tag,
            **kwargs,
        )

    @property
    def equity(self) -> float:
        return 0.0

    @property
    def exchange(self) -> Exchange:
        return self._exchange

    @property
    def data(self) -> DataFeed:
        return self._exchange.data

    @property
    def datas(self) -> list[DataFeed]:
        return self._exchange.datas

    @property
    def positions(self) -> Position:
        return self._exchange.positions

    @property
    def orders(self) -> pd.Series:
        return self._exchange.orders

    @property
    def history_orders(self) -> pd.Series:
        return self._exchange.history_orders

    @property
    def trades(self) -> pd.Series:
        return self._exchange.trades

    @property
    def positions(self) -> pd.Series:
        return self._exchange.positions

    @property
    def history_trades(self) -> pd.Series:
        return self._exchange.history_trades

    # Events
    def on_transaction(self, o):
        pass

    def on_execute(self, execute: Execute):
        pass

    def on_order(self, order: Order):
        pass

    def on_trade(self, trade: Trade):
        pass

    def on_position(self, position: Position):
        pass
