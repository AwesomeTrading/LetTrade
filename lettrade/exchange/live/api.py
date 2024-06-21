import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Optional

logger = logging.getLogger(__name__)


class LiveAPI(ABC):
    @classmethod
    def multiprocess(cls, kwargs: dict, **other_kwargs):
        """"""

    def __init__(self, **kwargs):
        """"""

    def init(self, **kwargs):
        """"""

    def start(self, exchange=None):
        """"""

    def next(self):
        """"""

    def stop(self):
        """"""

    # Public
    @abstractmethod
    def heartbeat(self):
        """"""

    # Market
    @abstractmethod
    def market(self, symbol: str):
        """"""

    @abstractmethod
    def markets(self, symbols: list[str]):
        """"""

    # Bars
    @abstractmethod
    def bars(self, **kwargs):
        """"""

    # Tick
    @abstractmethod
    def tick_get(self, symbol):
        """"""

    ### Private
    # Account
    @abstractmethod
    def account(self):
        """"""

    #  Order
    @abstractmethod
    def orders_total(
        self,
        since: Optional[datetime] = None,
        to: Optional[datetime] = None,
        **kwargs,
    ) -> int:
        """"""

    @abstractmethod
    def orders_get(
        self,
        id: Optional[str] = None,
        symbol: Optional[str] = None,
        **kwargs,
    ):
        """"""

    @abstractmethod
    def order_open(self, **kwargs):
        """"""

    @abstractmethod
    def order_update(self, order: "LiveOrder", sl=None, tp=None, **kwargs):
        """"""

    @abstractmethod
    def order_close(self, order: "LiveOrder", **kwargs):
        """"""

    # Execution
    @abstractmethod
    def executions_total(
        self,
        since: Optional[datetime] = None,
        to: Optional[datetime] = None,
        **kwargs,
    ) -> int:
        """"""

    @abstractmethod
    def executions_get(
        self,
        position_id: Optional[str] = None,
        search: Optional[str] = None,
        **kwargs,
    ) -> list[Any]:
        """"""

    @abstractmethod
    def execution_get(self, id: str, **kwargs) -> Any:
        """"""

    # Position
    @abstractmethod
    def positions_total(
        self,
        since: Optional[datetime] = None,
        to: Optional[datetime] = None,
        **kwargs,
    ) -> int:
        """"""

    @abstractmethod
    def positions_get(self, **kwargs):
        """"""

    @abstractmethod
    def position_update(
        self,
        position: "LivePosition",
        sl: Optional[float] = None,
        tp: Optional[float] = None,
        **kwargs,
    ):
        """"""

    @abstractmethod
    def position_close(self, position: "LivePosition", **kwargs):
        """"""
