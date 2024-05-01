from datetime import datetime
from typing import Optional, Tuple, Union

import numpy as np
import pandas as pd

from .base import BaseTransaction, State
from .order import Order


class Trade(BaseTransaction):
    """
    When an `Order` is filled, it results in an active `Trade`.
    Find active trades in `Strategy.trades` and closed, settled trades in `Strategy.closed_trades`.
    """

    def __init__(
        self,
        id: str,
        exchange: "Exchange",
        data: "DataFeed",
        size: float,
        entry_price: float,
        parent: "Order",
        created_at: datetime = None,
        entry_bar=None,
        tag: str = "",
        state: State = State.Open,
    ):
        super().__init__(
            id=id,
            exchange=exchange,
            data=data,
            size=size,
            created_at=created_at,
        )

        self.__entry_price = entry_price
        self.__state = state
        self.__tag = tag
        self.__parent: "Order" = parent

        self.__exit_price: Optional[float] = None
        self.__entry_bar: int = entry_bar
        self.__exit_bar: Optional[int] = None
        self.__sl_order: Optional[Order] = None
        self.__tp_order: Optional[Order] = None

    def __repr__(self):
        return f"<Trade id={self.id} size={self.size}>"
        # return (
        #     f'<Trade id={self.__id} size={self.__size} time={self.__entry_bar}-{self.__exit_bar or ""} '
        #     f'price={self.__entry_price}-{self.__exit_price or ""} pl={self.pl:.0f}'
        #     f'{" tag="+str(self.__tag) if self.__tag is not None else ""}>'
        # )

    # Fields getters
    @property
    def state(self) -> State:
        return self.__state

    @property
    def entry_price(self) -> float:
        """Trade entry price."""
        return self.__entry_price

    @property
    def exit_price(self) -> Optional[float]:
        """Trade exit price (or None if the trade is still active)."""
        return self.__exit_price

    @property
    def entry_bar(self) -> int:
        """Candlestick bar index of when the trade was entered."""
        return self.__entry_bar

    @property
    def exit_bar(self) -> Optional[int]:
        """
        Candlestick bar index of when the trade was exited
        (or None if the trade is still active).
        """
        return self.__exit_bar

    @property
    def tag(self):
        """
        A tag value inherited from the `Order` that opened
        this trade.

        This can be used to track trades and apply conditional
        logic / subgroup analysis.

        See also `Order.tag`.
        """
        return self.__tag

    @property
    def _sl_order(self):
        return self.__sl_order

    @property
    def _tp_order(self):
        return self.__tp_order

    # Extra properties
    @property
    def entry_time(self) -> Union[pd.Timestamp, int]:
        """Datetime of when the trade was entered."""
        return self.__exchange.data.index[self.__entry_bar]

    @property
    def exit_time(self) -> Optional[Union[pd.Timestamp, int]]:
        """Datetime of when the trade was exited."""
        if self.__exit_bar is None:
            return None
        return self.__exchange._data.index[self.__exit_bar]

    @property
    def is_long(self):
        """True if the trade is long (trade size is positive)."""
        return self.__size > 0

    @property
    def is_short(self):
        """True if the trade is short (trade size is negative)."""
        return not self.is_long

    @property
    def pl(self):
        """Trade profit (positive) or loss (negative) in cash units."""
        price = self.__exit_price or self.__exchange.last_price
        return self.__size * (price - self.__entry_price)

    @property
    def pl_pct(self):
        """Trade profit (positive) or loss (negative) in percent."""
        price = self.__exit_price or self.__exchange.last_price
        return copysign(1, self.__size) * (price / self.__entry_price - 1)

    @property
    def value(self):
        """Trade total value in cash (volume × price)."""
        price = self.__exit_price or self.__exchange.last_price
        return abs(self.__size) * price

    # SL/TP management API

    @property
    def sl(self):
        """
        Stop-loss price at which to close the trade.

        This variable is writable. By assigning it a new price value,
        you create or modify the existing SL order.
        By assigning it `None`, you cancel it.
        """
        return self.__sl_order and self.__sl_order.stop

    @sl.setter
    def sl(self, price: float):
        self.__set_contingent("sl", price)

    @property
    def tp(self):
        """
        Take-profit price at which to close the trade.

        This property is writable. By assigning it a new price value,
        you create or modify the existing TP order.
        By assigning it `None`, you cancel it.
        """
        return self.__tp_order and self.__tp_order.limit

    @tp.setter
    def tp(self, price: float):
        self.__set_contingent("tp", price)

    def __set_contingent(self, type, price):
        assert type in ("sl", "tp")
        assert price is None or 0 < price < np.inf
        attr = f"_{self.__class__.__qualname__}__{type}_order"
        order: Order = getattr(self, attr)
        if order:
            order.cancel()
        if price:
            kwargs = {"stop": price} if type == "sl" else {"limit": price}
            order = self.__exchange.new_order(
                -self.size, trade=self, tag=self.tag, **kwargs
            )
            setattr(self, attr, order)
