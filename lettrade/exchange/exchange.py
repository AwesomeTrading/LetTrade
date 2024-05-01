from abc import ABCMeta, abstractmethod
from datetime import datetime
from typing import Optional

import pandas as pd

from lettrade.base import BaseDataFeeds
from lettrade.commission import Commission
from lettrade.data import DataFeed, DataFeeder

from .base import OrderType, State
from .execute import Execute
from .order import Order
from .position import Position
from .trade import Trade


class Exchange(BaseDataFeeds, metaclass=ABCMeta):
    brain: "Brain"

    def __init__(self):
        self.feeder: DataFeeder = None
        self.commission: Commission = None
        self.cash: float = 0
        self.hedging: bool = False

        self.executes: pd.Series = pd.Series(dtype=object)
        self.orders: pd.Series = pd.Series(dtype=object)
        self.history_orders: pd.Series = pd.Series(dtype=object)
        self.trades: pd.Series = pd.Series(dtype=object)
        self.history_trades: pd.Series = pd.Series(dtype=object)
        self.positions: pd.Series = pd.Series(dtype=object)

    def next(self):
        pass

    def on_execute(self, execute: Execute, broadcast=True, *args, **kwargs):
        self.executes[execute.id] = execute

        if broadcast:
            self.brain.on_execute(execute)

    def on_order(self, order: Order, broadcast=True, *args, **kwargs):
        if order.state == State.Close:
            self.history_orders[order.id] = order
        else:
            self.orders[order.id] = order

        if broadcast:
            self.brain.on_order(order)

    def on_trade(self, trade: Trade, broadcast=True, *args, **kwargs):
        if trade.state == State.Close:
            self.history_trades[trade.id] = trade
        else:
            self.trades[trade.id] = trade

        if broadcast:
            self.brain.on_trade(trade)

    def on_position(self, position: Position, broadcast=True, *args, **kwargs):
        self.positions[position.id] = position

        if broadcast:
            self.brain.on_position(position)

    @abstractmethod
    def new_order(
        self,
        size: float,
        limit: Optional[float] = None,
        stop: Optional[float] = None,
        sl: Optional[float] = None,
        tp: Optional[float] = None,
        tag: object = None,
        *args,
        **kwargs
    ):
        raise NotImplementedError("Exchange.new_order not implement yet")

    # Alias
    @property
    def now(self) -> datetime:
        return self.data.now
