from abc import ABCMeta, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Optional

from lettrade.account import Account
from lettrade.commander import Commander
from lettrade.data import DataFeed, DataFeeder

from .base import OrderState, TradeState
from .execute import Execute
from .order import Order, OrderResult
from .position import Position
from .trade import Trade

# from lettrade.brain import Brain


class ExchangeState(int, Enum):
    Init = 1
    Start = 2
    Run = 3
    Stop = 4


class Exchange(metaclass=ABCMeta):
    """Base Exchange class to handle trading"""

    datas: list[DataFeed]
    """List of all available DataFeed"""
    data: DataFeed
    """main DataFeed"""

    executes: dict[str, Execute]
    """Execute dict by `Execute.id` key"""
    orders: dict[str, Order]
    """Available Order dict by `Order.id` key"""
    history_orders: dict[str, Order]
    """History Order dict by `Order.id` key"""
    trades: dict[str, Trade]
    """Available Trade dict by `Trade.id` key"""
    history_trades: dict[str, Trade]
    """History Order dict by `Order.id` key"""
    positions: dict[str, Position]
    """Available Position dict by `Position.id` key"""

    _brain: "Brain"
    _feeder: DataFeeder
    _account: Account
    _commander: Commander

    _state: ExchangeState

    def __init__(self):
        self.executes = dict()
        self.orders = dict()
        self.history_orders = dict()
        self.trades = dict()
        self.history_trades = dict()
        self.positions = dict()

        self._state = ExchangeState.Init

    def init(
        self,
        brain: "Brain",
        feeder: DataFeeder,
        account: Account,
        commander: Commander,
    ) -> None:
        """Init Exchange dependencies.
        Set data/datas from feeder.
        Set state to `ExchangeState.Start`.

        Args:
            brain (Brain): _description_
            feeder (DataFeeder): _description_
            account (Account): _description_
            commander (Commander): _description_
        """
        self._brain = brain
        self._feeder = feeder
        self._account = account
        self._commander = commander

        self.data = self._feeder.data
        self.datas = self._feeder.datas

        self._account.init(exchange=self)

        self._state = ExchangeState.Start

    def start(self) -> None:
        """Start of Exchange by:
        - Start account.
        - Set state to `ExchangeState.Run` ready for next().
        """
        self._account.start()
        self._state = ExchangeState.Run

    def next(self):
        "Call after data feeded and before strategy.next()"

    def next_next(self):
        "Call after strategy.next()"
        self._account._snapshot_equity()

    def stop(self) -> None:
        """Stop Exchange"""
        self._state = ExchangeState.Stop
        self._account.stop()

    def on_execute(
        self,
        execute: Execute,
        broadcast: Optional[bool] = True,
        **kwargs,
    ) -> None:
        """
        Receive Execute event from exchange then store and notify Brain
        """
        if not isinstance(execute, Execute):
            raise RuntimeError(f"{execute} is not instance of type Execute")

        if execute.id in self.executes:
            # Merge to keep Execute handler for strategy using
            # when strategy want to store Execute object
            # and object will be automatic update directly
            self.executes[execute.id].merge(execute)
            execute = self.executes[execute.id]
        else:
            self.executes[execute.id] = execute

        if self._state != ExchangeState.Run:
            return

        if broadcast:
            self._brain.on_execute(execute)

    def on_order(
        self,
        order: Order,
        broadcast: Optional[bool] = True,
        **kwargs,
    ) -> None:
        """
        Receive Order event from exchange then store and notify Brain
        """
        if not isinstance(order, Order):
            raise RuntimeError(f"{order} is not instance of type Order")

        if order.state in [OrderState.Executed, OrderState.Canceled]:
            self.history_orders[order.id] = order
            if order.id in self.orders:
                del self.orders[order.id]
        else:
            if order.id in self.history_orders:
                raise RuntimeError(f"Order {order.id} closed")

            if order.id in self.orders:
                # Merge to keep Order handler for strategy using
                # when strategy want to store Order object
                # and object will be automatic update directly
                self.orders[order.id].merge(order)
                order = self.orders[order.id]
            else:
                self.orders[order.id] = order

        if self._state != ExchangeState.Run:
            return

        if broadcast:
            self._brain.on_order(order)

    def on_trade(
        self,
        trade: Trade,
        broadcast: Optional[bool] = True,
        *args,
        **kwargs,
    ) -> None:
        """Receive Trade event from exchange then store and notify Brain

        Args:
            trade (Trade): new comming `Trade`
            broadcast (Optional[bool], optional): Flag notify for Brain. Defaults to True.

        Raises:
            RuntimeError: validat `Trade` instance
        """
        if not isinstance(trade, Trade):
            raise RuntimeError(f"{trade} is not instance of type Trade")

        if trade.state == TradeState.Exit:
            self.history_trades[trade.id] = trade
            if trade.id in self.trades:
                del self.trades[trade.id]

            self._account._on_trade_exit(trade)
        else:
            if trade.id in self.history_trades:
                raise RuntimeError(f"Order {trade.id} closed")
            if trade.id in self.trades:
                # Merge to keep Trade handler for strategy using
                # when strategy want to store Trade object
                # and object will be automatic update directly
                self.trades[trade.id].merge(trade)
                trade = self.trades[trade.id]
            else:
                self.trades[trade.id] = trade

        if self._state != ExchangeState.Run:
            return

        if broadcast:
            self._brain.on_trade(trade)

    def on_position(
        self,
        position: Position,
        broadcast: Optional[bool] = True,
        *args,
        **kwargs,
    ) -> None:
        """Receive Position event from exchange then store and notify Brain


        Args:
            position (Position): _description_
            broadcast (Optional[bool], optional): _description_. Defaults to True.

        Raises:
            RuntimeError: check `Position` instance
        """
        if not isinstance(position, Position):
            raise RuntimeError(f"{position} is not instance of type Position")

        if position.id in self.positions:
            # Merge to keep Position handler for strategy using
            # when strategy want to store Position object
            # and object will be automatic update directly
            self.positions[position.id].merge(position)
        else:
            self.positions[position.id] = position

        if self._state != ExchangeState.Run:
            return

        if broadcast:
            self._brain.on_position(position)

    def on_notify(self, *args, **kwargs):
        return self._brain.on_notify(*args, **kwargs)

    @abstractmethod
    def new_order(
        self,
        size: float,
        limit: Optional[float] = None,
        stop: Optional[float] = None,
        sl: Optional[float] = None,
        tp: Optional[float] = None,
        tag: Optional[object] = None,
        *args,
        **kwargs,
    ) -> OrderResult:
        """Place new `Order`

        Args:
            size (float): _description_
            limit (Optional[float], optional): _description_. Defaults to None.
            stop (Optional[float], optional): _description_. Defaults to None.
            sl (Optional[float], optional): _description_. Defaults to None.
            tp (Optional[float], optional): _description_. Defaults to None.
            tag (Optional[object], optional): _description_. Defaults to None.

        Returns:
            OrderResult: _description_
        """
        raise NotImplementedError("Exchange.new_order not implement yet")

    # Alias
    @property
    def now(self) -> datetime:
        return self.data.now
