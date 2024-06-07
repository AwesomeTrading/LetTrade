import logging
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class OrderSide(int, Enum):
    Buy = 1
    Sell = -1


class OrderState(str, Enum):
    Pending = "pending"
    Placed = "place"
    Executed = "executed"
    Canceled = "canceled"


class TradeState(str, Enum):
    Open = "open"
    Exit = "exit"


class OrderType(str, Enum):
    Market = "market"
    Limit = "limit"
    Stop = "stop"


class BaseTransaction:
    def __init__(
        self,
        id: str,
        exchange: "Exchange",
        data: "DataFeed",
        size: float,
    ) -> None:
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
