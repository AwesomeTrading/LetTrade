import logging
from typing import TYPE_CHECKING

from .base import BaseTransaction

if TYPE_CHECKING:
    from lettrade.data import DataFeed

    from .exchange import Exchange
    from .order import Order
    from .position import Position

logger = logging.getLogger(__name__)


class Execution(BaseTransaction):
    """Execution"""

    def __init__(
        self,
        id: str,
        exchange: "Exchange",
        data: "DataFeed",
        size: float,
        price: float,
        at: float,
        order_id: str | None = None,
        order: "Order | None" = None,
        position_id: str | None = None,
        position: "Position | None" = None,
        **kwargs,
    ):
        super().__init__(
            id=id,
            exchange=exchange,
            data=data,
            size=size,
            **kwargs,
        )
        self.order_id = order_id
        self.order: "Order" = order
        self.position_id = position_id
        self.position: "Position" = position
        self.price = price
        self.at = at

    def __repr__(self):
        return f"<{self.__class__.__name__} id={self.id} size={self.size}>"

    def _on_execution(self):
        self.exchange.on_execution(self)

    def merge(self, other: "Execution"):
        """
        Merge to keep object handler but not overwrite for Strategy using when Strategy want to store object and object will be automatic update directly
        """
        if other is self:
            return

        if self.id != other.id:
            raise RuntimeError(f"Merge difference id {self.id} != {other.id} execution")

        self.price = other.price
        self.size = other.size

        if other.at:
            self.at = other.at
        if other.order_id:
            self.order_id = other.order_id
        if other.order:
            self.order = other.order
        if other.position_id:
            self.position_id = other.position_id
        if other.position:
            self.position = other.position
