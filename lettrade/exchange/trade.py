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
        entry_at: Optional[int] = None,
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
        self.entry_at: Optional[int] = entry_at
        self.exit_price: Optional[float] = None
        self.exit_at: Optional[int] = None
        self.exit_pl: Optional[float] = None
        self.exit_fee: Optional[float] = None
        self.sl_order: Optional[Order] = sl_order
        self.tp_order: Optional[Order] = tp_order

    def __repr__(self):
        return f"<Trade id={self.id} state={self.state} size={self.size}>"
        # return (
        #     f'<Trade id={self.id} size={self.size} time={self.entry_at}-{self.exit_at or ""} '
        #     f'price={self.entry_price}-{self.exit_price or ""} pl={self.pl:.0f}'
        #     f'{" tag="+str(self.tag) if self.tag is not None else ""}>'
        # )

    def entry(self, price, at) -> bool:
        self.entry_price = price
        self.entry_at: int = at
        self.state = TradeState.Open
        self.exchange.on_trade(self)
        return True

    def exit(self, price, at, pl, fee) -> bool:
        if self.state != TradeState.Open:
            return False

        self.exit_price = price
        self.exit_at = at
        self.exit_pl = pl
        self.exit_fee = fee
        self.state = TradeState.Exit
        self.exchange.on_trade(self)
        return True

    def merge(self, other: "Trade"):
        if other is self:
            return

        if self.id != other.id:
            raise RuntimeError(f"Merge difference id {self.id} != {other.id} order")

        self.size = other.size
        if other.sl_order:
            self.sl_order = other.sl_order
        if other.tp_order:
            self.tp_order = other.tp_order

        if other.entry_price:
            self.entry_price = other.entry_price
        if other.entry_at:
            self.entry_at = other.entry_at

        if other.exit_price:
            self.exit_price = other.exit_price
        if other.exit_at:
            self.exit_at = other.exit_at
        if other.parent:
            self.parent = other.parent

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
