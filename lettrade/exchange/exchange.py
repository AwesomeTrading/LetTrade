from abc import ABCMeta, abstractmethod
from typing import Optional

from lettrade.base import BaseDataFeeds
from lettrade.data import DataFeed, DataFeeder

from .base import FastQuery
from .execute import Execute
from .order import Order
from .position import Position
from .trade import Trade


class Exchange(BaseDataFeeds, metaclass=ABCMeta):
    _brain: "Brain"

    def __init__(self):
        self.feeder: DataFeeder = None

        self.__executes: FastQuery[Execute] = FastQuery[Execute]()
        self.__orders: FastQuery[Order] = FastQuery[Order]()
        self.__trades: FastQuery[Trade] = FastQuery[Trade]()
        self.__positions: FastQuery[Position] = FastQuery[Position]()

    def _on_order(self, order: Order, broadcast=True, *args, **kwargs):
        self.__orders.add(order)

        if broadcast:
            self._brain._on_order(order)

    def _on_execute(self, execute: Execute, broadcast=True, *args, **kwargs):
        self.__executes.add(execute)

        if broadcast:
            self._brain._on_execute(execute)

    def _on_trade(self, trade: Trade, broadcast=True, *args, **kwargs):
        self.__trades.add(trade)

        if broadcast:
            self._brain._on_trade(trade)

    def _on_position(self, position: Position, broadcast=True, *args, **kwargs):
        self.__positions.add(position)

        if broadcast:
            self._brain._on_position(position)

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
