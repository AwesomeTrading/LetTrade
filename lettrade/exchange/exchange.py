from abc import ABCMeta, abstractmethod
from datetime import datetime
from typing import Optional

import pandas as pd

from lettrade.account import Account
from lettrade.base import BaseDataFeeds
from lettrade.data import DataFeeder

from .base import OrderState, TradeState
from .execute import Execute
from .order import Order
from .position import Position
from .trade import Trade


class Exchange(BaseDataFeeds, metaclass=ABCMeta):
    _brain: "Brain"
    _feeder: DataFeeder
    _account: Account

    def __init__(self):
        self.executes: dict[str, Execute] = dict()
        self.orders: dict[str, Order] = dict()
        self.history_orders: dict[str, Order] = dict()
        self.trades: dict[str, Trade] = dict()
        self.history_trades: dict[str, Trade] = dict()
        self.positions: dict[str, Position] = dict()

    def init(self, brain: "Brain", feeder: DataFeeder, account: Account):
        self._brain = brain
        self._feeder = feeder
        self._account = account

        self._account.init(exchange=self)

    @property
    def feeder(self) -> DataFeeder:
        return self._feeder

    def next(self):
        self._account.snapshot_equity()

    def on_execute(self, execute: Execute, broadcast=True, *args, **kwargs):
        self.executes[execute.id] = execute

        if broadcast:
            self._brain.on_execute(execute)

    def on_order(self, order: Order, broadcast=True, *args, **kwargs):
        if order.state in [OrderState.Executed, OrderState.Canceled]:
            self.history_orders[order.id] = order
            if order.id in self.orders:
                # self.orders = self.orders.drop(index=order.id)
                del self.orders[order.id]
        else:
            if order.id in self.history_orders:
                raise RuntimeError(f"Order {order.id} closed")
            self.orders[order.id] = order

        if broadcast:
            self._brain.on_order(order)

    def on_trade(self, trade: Trade, broadcast=True, *args, **kwargs):
        if trade.state == TradeState.Exit:
            self.history_trades[trade.id] = trade
            if trade.id in self.trades:
                # self.trades = self.trades.drop(index=trade.id)
                del self.trades[trade.id]
        else:
            if trade.id in self.history_trades:
                raise RuntimeError(f"Order {trade.id} closed")
            self.trades[trade.id] = trade

        if broadcast:
            self._brain.on_trade(trade)

    def on_position(self, position: Position, broadcast=True, *args, **kwargs):
        self.positions[position.id] = position

        if broadcast:
            self._brain.on_position(position)

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
        **kwargs,
    ):
        raise NotImplementedError("Exchange.new_order not implement yet")

    # Alias
    @property
    def now(self) -> datetime:
        return self.data.now
