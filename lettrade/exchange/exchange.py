import logging
from abc import ABCMeta, abstractmethod
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional

from lettrade.account import Account
from lettrade.commander import Commander
from lettrade.data import DataFeed, DataFeeder

from .execution import Execution
from .order import Order, OrderResult
from .position import Position

if TYPE_CHECKING:
    from lettrade.brain import Brain


logger = logging.getLogger(__name__)


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

    executions: dict[str, Execution]
    """Execution dict by `Execution.id` key"""
    orders: dict[str, Order]
    """Available Order dict by `Order.id` key"""
    history_orders: dict[str, Order]
    """History Order dict by `Order.id` key"""
    positions: dict[str, Position]
    """Available Position dict by `Position.id` key"""
    history_positions: dict[str, Position]
    """History Position dict by `Position.id` key"""

    _config: dict

    _brain: "Brain"
    _feeder: DataFeeder
    _account: Account
    _commander: Commander

    _state: ExchangeState

    def __init__(self, **kwargs):
        self._config = kwargs

        self.orders = dict()
        self.history_orders = dict()
        self.positions = dict()
        self.history_positions = dict()

        # Disable Execution by defaul
        if self._config.setdefault("use_execution", False):
            self.executions = dict()
        else:
            self.executions = None

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
        self._account._equity_snapshot()

    def stop(self) -> None:
        """Stop Exchange"""
        self._state = ExchangeState.Stop
        self._account.stop()

    def on_execution(
        self,
        execution: Execution,
        broadcast: Optional[bool] = True,
        **kwargs,
    ) -> None:
        """
        Receive Execution event from exchange then store and notify Brain
        """
        if self.executions is None:
            logger.warning(
                "Execution transaction is disable, enable by flag: show_execution=True"
            )
            return

        if not isinstance(execution, Execution):
            raise RuntimeError(f"{execution} is not instance of type Execution")

        if execution.id in self.executions:
            # Merge to keep Execution handler for strategy using
            # when strategy want to store Execution object
            # and object will be automatic update directly
            self.executions[execution.id].merge(execution)
            execution = self.executions[execution.id]
        else:
            self.executions[execution.id] = execution

        if self._state != ExchangeState.Run:
            return

        if broadcast:
            self._brain.on_execution(execution)

    def on_order(
        self,
        order: Order,
        broadcast: Optional[bool] = True,
        **kwargs,
    ) -> None:
        """Receive Order event from exchange then store and notify Brain"""
        if not isinstance(order, Order):
            raise RuntimeError(f"{order} is not instance of type Order")

        if order.is_closed:
            if order.id in self.history_orders:
                logger.warning("Order closed recall: %s", order)

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

    def on_position(
        self,
        position: Position,
        broadcast: Optional[bool] = True,
        **kwargs,
    ) -> None:
        """Receive Position event from exchange then store and notify Brain

        Args:
            position (Position): new comming `Position`
            broadcast (Optional[bool], optional): Flag notify for Brain. Defaults to True.

        Raises:
            RuntimeError: validat `Position` instance
        """
        if not isinstance(position, Position):
            raise RuntimeError(f"{position} is not instance of type Position")

        if position.is_exited:
            if position.id in self.history_positions:
                logger.warning("Position exited recall: %s", position)

            self.history_positions[position.id] = position
            if position.id in self.positions:
                del self.positions[position.id]

            self._account._on_position_exit(position)
        else:
            if position.id in self.history_positions:
                raise RuntimeError(f"Position {position.id} closed: {position}")
            if position.id in self.positions:
                # Merge to keep Position handler for strategy using
                # when strategy want to store Position object
                # and object will be automatic update directly
                self.positions[position.id].merge(position)
                position = self.positions[position.id]
            else:
                self.positions[position.id] = position
                self._account._on_position_entry(position)

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
