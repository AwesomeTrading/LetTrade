from datetime import datetime
from typing import Callable, Dict, List, Optional, Sequence, Set, Tuple, Type, Union

from .base import BaseTransaction, OrderState, OrderType


class Order(BaseTransaction):
    _trade_cls: Type["Trade"] = None
    _execute_cls: Type["Execute"] = None

    def __init__(
        self,
        id: str,
        exchange: "Exchange",
        data: "DataFeed",
        size: float,
        state: OrderState = OrderState.Pending,
        type: OrderType = OrderType.Market,
        limit_price: Optional[float] = None,
        stop_price: Optional[float] = None,
        sl_price: Optional[float] = None,
        tp_price: Optional[float] = None,
        trade: Optional["Trade"] = None,
        parent: Optional["Order"] = None,
        tag: object = None,
        open_bar: int = None,
        open_price: int = None,
    ):
        super().__init__(
            id=id,
            exchange=exchange,
            data=data,
            size=size,
        )

        self.type: OrderType = type
        self.state: OrderState = state
        self.limit_price: Optional[float] = limit_price
        self.stop_price: Optional[float] = stop_price
        self.sl_price: Optional[float] = sl_price
        self.tp_price: Optional[float] = tp_price
        self.trade: Optional["Trade"] = trade
        self.parent: Optional["Order"] = parent
        self.tag: object = tag

        self.open_bar: int = open_bar
        self.open_price: int = open_price
        self.entry_bar: int = None
        self.entry_price: int = None

    def __repr__(self):
        return "<Order {}>".format(
            ", ".join(
                f"{param}={value if isinstance(value, str) else round(value, 5)}"
                for param, value in (
                    ("id", self.id),
                    ("type", self.type),
                    ("state", self.state),
                    ("size", self.size),
                    ("limit", self.limit_price),
                    ("stop", self.stop_price),
                    ("sl", self.sl_price),
                    ("tp", self.tp_price),
                    ("tag", self.tag),
                )
                if value is not None
            )
        )

    def execute(self, price, bar):
        self.entry_bar = bar
        self.entry_price = price
        self.state = OrderState.Executed
        self.exchange.on_order(self)

    # Fields getters
    @property
    def limit(self) -> Optional[float]:
        return self.limit_price

    @property
    def stop(self) -> Optional[float]:
        return self.stop_price

    @property
    def sl(self) -> Optional[float]:
        return self.sl_price

    @property
    def tp(self) -> Optional[float]:
        return self.tp_price

    # Extra properties
    @property
    def is_long(self):
        """True if the order is long (order size is positive)."""
        return self.size > 0

    @property
    def is_short(self):
        """True if the order is short (order size is negative)."""
        return self.size < 0

    @property
    def is_sl_order(self):
        return self.trade and self is self.trade.sl_order

    @property
    def is_tp_order(self):
        return self.trade and self is self.trade.tp_order
