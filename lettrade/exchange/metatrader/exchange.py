import logging
from typing import Optional

from lettrade.data import DataFeed
from lettrade.exchange import Exchange, OrderType

logger = logging.getLogger(__name__)

from .api import MetaTraderAPI


class MetaTraderExchange(Exchange):
    _api: MetaTraderAPI

    def __init__(self, api: MetaTraderAPI, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._api = api

    def next(self):
        super().next()

    def new_order(
        self,
        size: float,
        type: OrderType = OrderType.Market,
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

        if type == OrderType.Market:
            limit = 0
            stop = 0

        order = MetaTraderOrder(
            id=self._id(),
            exchange=self,
            data=data,
            size=size,
            type=type,
            limit_price=limit,
            stop_price=stop,
            sl_price=sl,
            tp_price=tp,
            tag=tag,
            open_price=self.data.open[0],
            open_bar=self.data.bar(),
        )
        order.place()

        if __debug__:
            logger.info("New order %s at %s", order, self.data.now)
