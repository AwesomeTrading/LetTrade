from typing import Optional

from lettrade.data import DataFeed

from ..exchange import Exchange


class BackTestExchange(Exchange):
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
        print("New order:", size, limit, stop, sl, tp, tag)
        print(data[0])
