from abc import ABCMeta, abstractmethod
from typing import Optional

from lettrade.base import BaseDataFeeds
from lettrade.commission import Commission
from lettrade.data import DataFeed, DataFeeder

from .base import FastQuery
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

        self.executes: FastQuery[Execute] = FastQuery[Execute]()
        self.orders: FastQuery[Order] = FastQuery[Order]()
        self.trades: FastQuery[Trade] = FastQuery[Trade]()
        self.closed_trades: FastQuery[Trade] = FastQuery[Trade]()
        self.positions: FastQuery[Position] = FastQuery[Position]()

    def on_execute(self, execute: Execute, broadcast=True, *args, **kwargs):
        self.executes.add(execute)

        if broadcast:
            self.brain.on_execute(execute)

    def on_order(self, order: Order, broadcast=True, *args, **kwargs):
        self.orders.add(order)

        if broadcast:
            self.brain.on_order(order)

    def on_trade(self, trade: Trade, broadcast=True, *args, **kwargs):
        self.trades.add(trade)

        if broadcast:
            self.brain.on_trade(trade)

    def on_position(self, position: Position, broadcast=True, *args, **kwargs):
        self.positions.add(position)

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
