from datetime import datetime
from enum import Enum
from typing import Generic, TypeVar

T = TypeVar("T")


class State(str, Enum):
    Open = "open"
    Pending = "pending"
    Close = "close"


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

    def _replace(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, f"_{self.__class__.__qualname__}__{k}", v)
        return self
