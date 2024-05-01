from datetime import datetime
from typing import Callable, Dict, List, Optional, Sequence, Set, Tuple, Type, Union

from .base import BaseTransaction, OrderType, State


class Order(BaseTransaction):
    def __init__(
        self,
        id: str,
        exchange: "Exchange",
        data: "DataFeed",
        size: float,
        created_at: datetime = None,
        state: State = State.Open,
        type: OrderType = OrderType.Market,
        limit_price: Optional[float] = None,
        stop_price: Optional[float] = None,
        sl_price: Optional[float] = None,
        tp_price: Optional[float] = None,
        trade: Optional["Trade"] = None,
        parent: Optional["Order | Trade"] = None,
        tag: object = None,
    ):
        super().__init__(
            id=id,
            exchange=exchange,
            data=data,
            size=size,
            created_at=created_at,
        )

        self.__type = type
        self.__state = state
        self.__limit_price = limit_price
        self.__stop_price = stop_price
        self.__sl_price = sl_price
        self.__tp_price = tp_price
        self.__trade = trade
        self.__parent: "Order | Trade" = parent
        self.__tag = tag

        self._entry_bar: int = None
        self._entry_price: int = None
        self._sl_order: "Order" = None
        self._tp_order: "Order" = None

    def __repr__(self):
        return "<Order {}>".format(
            ", ".join(
                f"{param}={value if isinstance(value, str) else round(value, 5)}"
                for param, value in (
                    ("id", self.id),
                    ("size", self.size),
                    ("limit", self.__limit_price),
                    ("stop", self.__stop_price),
                    ("sl", self.__sl_price),
                    ("tp", self.__tp_price),
                    ("tag", self.__tag),
                )
                if value is not None
            )
        )

    def cancel(self):
        """Cancel the order."""
        self.__exchange.orders.remove(self)
        parent = self.__parent
        if self.__parent:
            if self is parent._sl_order:
                parent._replace(sl_order=None)
            elif self is parent._tp_order:
                parent._replace(tp_order=None)

    # Fields getters
    @property
    def type(self) -> OrderType:
        return self.__type

    @property
    def state(self) -> State:
        return self.__state

    @property
    def limit(self) -> Optional[float]:
        """
        Order limit price for [limit orders], or None for [market orders],
        which are filled at next available price.

        [limit orders]: https://www.investopedia.com/terms/l/limitorder.asp
        [market orders]: https://www.investopedia.com/terms/m/marketorder.asp
        """
        return self.__limit_price

    @property
    def stop(self) -> Optional[float]:
        """
        Order stop price for [stop-limit/stop-market][_] order,
        otherwise None if no stop was set, or the stop price has already been hit.

        [_]: https://www.investopedia.com/terms/s/stoporder.asp
        """
        return self.__stop_price

    @property
    def sl(self) -> Optional[float]:
        """
        A stop-loss price at which, if set, a new contingent stop-market order
        will be placed upon the `Trade` following this order's execution.
        See also `Trade.sl`.
        """
        return self.__sl_price

    @property
    def tp(self) -> Optional[float]:
        """
        A take-profit price at which, if set, a new contingent limit order
        will be placed upon the `Trade` following this order's execution.
        See also `Trade.tp`.
        """
        return self.__tp_price

    @property
    def parent(self) -> "Order | Trade":
        return self.__parent

    @property
    def tag(self):
        """
        Arbitrary value (such as a string) which, if set, enables tracking
        of this order and the associated `Trade` (see `Trade.tag`).
        """
        return self.__tag

    # Extra properties
    @property
    def is_long(self):
        """True if the order is long (order size is positive)."""
        return self.__size > 0

    @property
    def is_short(self):
        """True if the order is short (order size is negative)."""
        return self.__size < 0
