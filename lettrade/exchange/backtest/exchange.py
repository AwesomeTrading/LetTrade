from typing import Optional

from lettrade.data import DataFeed

from .. import Order, Position, Trade
from ..exchange import Exchange


class BackTestExchange(Exchange):
    __id = 0

    def new_order(
        self,
        size: float,
        limit: Optional[float] = None,
        stop: Optional[float] = None,
        sl: Optional[float] = None,
        tp: Optional[float] = None,
        tag: object = None,
        data: DataFeed = None,
        *args,
        **kwargs
    ):
        if not data:
            data = self.data

        self.__id += 1

        order = Order(
            id=str(self.__id),
            exchange=self,
            data=data,
            size=size,
            limit_price=limit,
            stop_price=stop,
            sl_price=stop,
            tp_price=tp,
            tag=tag,
        )
        self._on_order(order)
