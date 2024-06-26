import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .exchange import LiveExchange
    from .trade import LiveOrder, LivePosition

logger = logging.getLogger(__name__)


class LiveAPI(ABC):
    @classmethod
    def multiprocess(cls, kwargs: dict, **other_kwargs):
        """"""

    def __init__(self, **kwargs):
        """"""

    def init(self, **kwargs):
        """"""

    def start(self, exchange: "LiveExchange"):
        """"""

    def next(self):
        """"""

    def stop(self):
        """"""

    # Public
    def heartbeat(self) -> bool:
        """"""
        return True

    # Market
    @abstractmethod
    def market(self, symbol: str) -> dict:
        """"""

    @abstractmethod
    def markets(self, symbols: list[str]) -> dict:
        """"""

    # Bars
    @abstractmethod
    def bars(
        self,
        symbol,
        timeframe,
        since: int | datetime | None = 0,
        to: int | datetime | None = 1_000,
    ) -> list[list]:
        """"""

    # Tick
    @abstractmethod
    def tick_get(self, symbol: str) -> dict:
        """"""

    ### Private
    # Account
    @abstractmethod
    def account(self) -> dict:
        """"""

    #  Order
    @abstractmethod
    def orders_total(
        self,
        since: datetime | None = None,
        to: datetime | None = None,
        **kwargs,
    ) -> int:
        """"""

    @abstractmethod
    def orders_get(
        self,
        id: str | None = None,
        symbol: str | None = None,
        **kwargs,
    ):
        """"""

    @abstractmethod
    def order_open(self, **kwargs) -> dict:
        """"""

    @abstractmethod
    def order_update(self, order: "LiveOrder", sl=None, tp=None, **kwargs) -> dict:
        """"""

    @abstractmethod
    def order_close(self, order: "LiveOrder", **kwargs) -> dict:
        """"""

    def orders_history_get(
        self,
        id: str | None = None,
        since: datetime | None = None,
        to: datetime | None = None,
        **kwargs,
    ) -> list[dict]:
        """"""

    # Execution
    @abstractmethod
    def executions_total(
        self,
        since: datetime | None = None,
        to: datetime | None = None,
        **kwargs,
    ) -> int:
        """"""

    @abstractmethod
    def executions_get(
        self,
        position_id: str | None = None,
        search: str | None = None,
        **kwargs,
    ) -> list[dict]:
        """"""

    @abstractmethod
    def execution_get(self, id: str, **kwargs) -> dict:
        """"""

    # Position
    @abstractmethod
    def positions_total(
        self,
        since: datetime | None = None,
        to: datetime | None = None,
        **kwargs,
    ) -> int:
        """"""

    @abstractmethod
    def positions_get(self, id: str = None, symbol: str = None, **kwargs) -> list[dict]:
        """"""

    @abstractmethod
    def position_update(
        self,
        position: "LivePosition",
        sl: float | None = None,
        tp: float | None = None,
        **kwargs,
    ) -> dict:
        """"""

    @abstractmethod
    def position_close(self, position: "LivePosition", **kwargs) -> dict:
        """"""
