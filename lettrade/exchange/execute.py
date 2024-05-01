from datetime import datetime
from typing import Callable, Dict, List, Optional, Sequence, Tuple, Type, Union

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
        parent: "Order",
    ):
        super().__init__(
            id=id,
            exchange=exchange,
            data=data,
            size=size,
        )
        self.parent: "Order" = parent
        self.price = price

    def __repr__(self):
        return f"<Execute id={self.id} size={self.size}>"
