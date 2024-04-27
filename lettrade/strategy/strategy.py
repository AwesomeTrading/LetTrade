from abc import ABCMeta, abstractmethod
from typing import Optional, Tuple

from ..data import DataFeed
from ..exchange import Exchange
from ..trade import Order, Position, Trade


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
    def position(self) -> Position:
        return None

    @property
    def orders(self) -> Tuple[Order, ...]:
        return ()

    @property
    def trades(self) -> Tuple[Trade, ...]:
        return ()

    @property
    def closed_trades(self) -> Tuple[Trade, ...]:
        return ()
