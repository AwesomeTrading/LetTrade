import logging
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from lettrade import DataFeed, Exchange

logger = logging.getLogger(__name__)


class TradeSide(int, Enum):
    """Side of Trade"""

    Buy = 1
    """Buy/Long side"""
    Sell = -1
    """Sell/Short side"""

    def lower(self) -> str:
        return self.name.lower()

    def upper(self) -> str:
        return self.name.upper()


class OrderType(str, Enum):
    """Order type"""

    Market = "market"
    """Market order"""
    Limit = "limit"
    """Limit order"""
    Stop = "stop"
    """Stop order"""
    StopLimit = "stoplimit"
    """Stop-Limit order"""


class OrderState(str, Enum):
    """Order state"""

    Pending = "pending"
    """Pending order, wait for exchange accept"""
    Placed = "place"
    """Placed order on exchange"""
    Partial = "partial"
    """Partial filled, still wait for full fill"""
    Filled = "filled"
    """Full filled"""
    Canceled = "canceled"
    """Canceled"""


class PositionState(str, Enum):
    """Position state"""

    Open = "open"
    """Opening state"""
    Exit = "exit"
    """Exited state"""


class BaseTransaction:
    """Base class of Execution/Order/Position"""

    def __init__(
        self,
        id: str,
        exchange: "Exchange",
        data: "DataFeed",
        size: float,
    ) -> None:
        """_summary_

        Args:
            id (str): _description_
            exchange (Exchange): _description_
            data (DataFeed): _description_
            size (float): _description_
        """
        self.id: str = id
        self.exchange: "Exchange" = exchange
        self.data: "DataFeed" = data
        self.size: float = size

    @property
    def is_long(self) -> bool:
        """True if side is long (size is positive).

        Returns:
            bool: True/False
        """
        return self.size > 0

    @property
    def is_short(self) -> bool:
        """True if side is short (size is negative).

        Returns:
            bool: _description_
        """
        return self.size < 0

    @property
    def side(self) -> TradeSide:
        """True if side is short (size is negative).

        Returns:
            bool: _description_
        """
        return TradeSide.Sell if self.size < 0 else TradeSide.Buy


if __debug__:
    from lettrade.base.flag import validate_strategy_trade

    if validate_strategy_trade:

        import inspect

        def base_transaction__setattr__(self, name: str, value: Any) -> None:

            stack = inspect.stack()[1]
            caller_cls = stack[0].f_locals["self"].__class__

            from lettrade.strategy import Strategy

            if issubclass(caller_cls, Strategy):
                caller_method = stack[0].f_code.co_name
                logger.warning(
                    "Strategy %s.%s try to set %s=%s, run 'python -OO' to bypass warning",
                    caller_cls,
                    caller_method,
                    name,
                    value,
                )

            object.__setattr__(self, name, value)

        setattr(BaseTransaction, "__setattr__", base_transaction__setattr__)
