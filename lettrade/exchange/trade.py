from datetime import datetime
from typing import Optional, Tuple, Union

import numpy as np
import pandas as pd

from .base import BaseTransaction, TradeState
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
        parent: "Order",
        tag: object = "",
        state: TradeState = TradeState.Open,
        entry_price: Optional[float] = None,
        entry_bar: Optional[int] = None,
        sl_order: Optional[Order] = None,
        tp_order: Optional[Order] = None,
    ):
        super().__init__(
            id=id,
            exchange=exchange,
            data=data,
            size=size,
        )
        self._account = self.exchange._account

        self.state = state
        self.tag: object = tag
        self.parent: "Order" = parent

        self.entry_price: Optional[float] = entry_price
        self.entry_bar: Optional[int] = entry_bar
        self.exit_price: Optional[float] = None
        self.exit_bar: Optional[int] = None
        self.exit_pl: Optional[float] = None
        self.exit_fee: Optional[float] = None
        self.sl_order: Optional[Order] = sl_order
        self.tp_order: Optional[Order] = tp_order

    def __repr__(self):
        return f"<Trade id={self.id} state={self.state} size={self.size}>"
        # return (
        #     f'<Trade id={self.id} size={self.size} time={self.entry_bar}-{self.exit_bar or ""} '
        #     f'price={self.entry_price}-{self.exit_price or ""} pl={self.pl:.0f}'
        #     f'{" tag="+str(self.tag) if self.tag is not None else ""}>'
        # )

    def entry(self, price, bar) -> bool:
        self.entry_price = price
        self.entry_bar: int = bar
        self.state = TradeState.Open
        self.exchange.on_trade(self)
        return True

    def exit(self, price, bar, pl, fee) -> bool:
        if self.state != TradeState.Open:
            return False

        self.exit_price = price
        self.exit_bar = bar
        self.exit_pl = pl
        self.exit_fee = fee
        self.state = TradeState.Exit
        self.exchange.on_trade(self)
        return True

    # Extra properties
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
        if self.state == TradeState.Exit:
            return self.exit_pl

        return self._account.size_to_pl(size=self.size, entry_price=self.entry_price)

    @property
    def fee(self):
        if self.state == TradeState.Exit:
            return self.exit_fee

        return 0
