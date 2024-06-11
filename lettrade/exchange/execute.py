from typing import Optional

from .base import BaseTransaction


class Execute(BaseTransaction):
    """
    Place new orders through `Strategy.buy()` and `Strategy.sell()`.
    Query existing orders through `Strategy.orders`.

    When an order is executed or [filled], it results in a `Trade`.

    If you wish to modify aspects of a placed but not yet filled order,
    cancel it and place a new one instead.

    All placed orders are [Good 'Til Canceled].

    [filled]: https://www.investopedia.com/terms/f/fill.asp
    [Good 'Til Canceled]: https://www.investopedia.com/terms/g/gtc.asp
    """

    def __init__(
        self,
        id: str,
        exchange: "Exchange",
        data: "DataFeed",
        size: float,
        price: float,
        at: float,
        order_id: Optional[str] = None,
        order: Optional["Order"] = None,
        trade_id: Optional[str] = None,
        trade: Optional["Trade"] = None,
    ):
        super().__init__(
            id=id,
            exchange=exchange,
            data=data,
            size=size,
        )
        self.order_id = order_id
        self.order: "Order" = order
        self.trade_id = trade_id
        self.trade: "Trade" = trade
        self.price = price
        self.at = at

    def __repr__(self):
        return f"<Execute id={self.id} size={self.size}>"

    def _on_execute(self):
        self.exchange.on_execute(self)

    def merge(self, other: "Execute"):
        """
        Merge to keep object handler but not overwrite for Strategy using when Strategy want to store object and object will be automatic update directly
        """
        if other is self:
            return

        if self.id != other.id:
            raise RuntimeError(f"Merge difference id {self.id} != {other.id} execute")

        self.price = other.price
        self.size = other.size

        if other.at:
            self.at = other.at
        if other.order_id:
            self.order_id = other.order_id
        if other.order:
            self.order = other.order
        if other.trade_id:
            self.trade_id = other.trade_id
        if other.trade:
            self.trade = other.trade
