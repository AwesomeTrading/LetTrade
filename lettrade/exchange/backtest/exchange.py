from typing import Optional

from lettrade.data import DataFeed
from lettrade.exchange import Exchange, Order, Position, Trade


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
            sl_price=sl,
            tp_price=tp,
            tag=tag,
        )
        self.on_order(order)

        self.__id += 1
        trade = Trade(
            id=str(self.__id),
            exchange=self,
            data=data,
            size=size,
            tag=tag,
            entry_price=self.data.close[0],
            entry_bar=self.data[0],
        )
        self.on_trade(trade)
