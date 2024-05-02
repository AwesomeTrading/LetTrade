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
        entry_bar: int,
        parent: "Order",
        tag: object = "",
        state: State = State.Open,
        sl_order: Optional[Order] = None,
        tp_order: Optional[Order] = None,
    ):
        super().__init__(
            id=id,
            exchange=exchange,
            data=data,
            size=size,
        )
        self.state = state
        self.tag: object = tag
        self.parent: "Order" = parent

        self.entry_price = entry_price
        self.entry_bar: int = entry_bar
        self.exit_price: Optional[float] = None
        self.exit_bar: Optional[int] = None
        self.sl_order: Optional[Order] = sl_order
        self.tp_order: Optional[Order] = tp_order

    def __repr__(self):
        return f"<Trade id={self.id} state={self.state} size={self.size}>"
        # return (
        #     f'<Trade id={self.id} size={self.size} time={self.entry_bar}-{self.exit_bar or ""} '
        #     f'price={self.entry_price}-{self.exit_price or ""} pl={self.pl:.0f}'
        #     f'{" tag="+str(self.tag) if self.tag is not None else ""}>'
        # )

    def exit(self, price, bar):
        self.exit_price = price
        self.exit_bar = bar
        self.state = State.Close
        self.exchange.on_trade(self)

    # Extra properties
    @property
    def entry_time(self) -> Union[pd.Timestamp, int]:
        """Datetime of when the trade was entered."""
        return self.exchange.data.index[self.entry_bar]

    @property
    def exit_time(self) -> Optional[Union[pd.Timestamp, int]]:
        """Datetime of when the trade was exited."""
        if self.exit_bar is None:
            return None
        return self.exchange._data.index[self.exit_bar]

    @property
    def is_long(self):
        """True if the trade is long (trade size is positive)."""
        return self.size > 0

    @property
    def is_short(self):
        """True if the trade is short (trade size is negative)."""
        return not self.is_long

    @property
    def pl(self):
        """Trade profit (positive) or loss (negative) in cash units."""
        price = self.exit_price or self.exchange.last_price
        return self.size * (price - self.entry_price)

    @property
    def pl_pct(self):
        """Trade profit (positive) or loss (negative) in percent."""
        price = self.exit_price or self.exchange.last_price
        return copysign(1, self.size) * (price / self.entry_price - 1)

    @property
    def value(self):
        """Trade total value in cash (volume × price)."""
        price = self.exit_price or self.exchange.last_price
        return abs(self.size) * price

    # SL/TP management API
    @property
    def sl(self):
        """
        Stop-loss price at which to close the trade.

        This variable is writable. By assigning it a new price value,
        you create or modify the existing SL order.
        By assigning it `None`, you cancel it.
        """
        return self.sl_order and self.sl_order.stop

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
        return self.tp_order and self.tp_order.limit

    @tp.setter
    def tp(self, price: float):
        self.__set_contingent("tp", price)

    def __set_contingent(self, type, price):
        assert type in ("sl", "tp")
        assert price is None or 0 < price < np.inf
        attr = f"_{self.class__.__qualname__}__{type}_order"
        order: Order = getattr(self, attr)
        if order:
            order.cancel()
        if price:
            kwargs = {"stop": price} if type == "sl" else {"limit": price}
            order = self.exchange.new_order(
                -self.size, trade=self, tag=self.tag, **kwargs
            )
            setattr(self, attr, order)
