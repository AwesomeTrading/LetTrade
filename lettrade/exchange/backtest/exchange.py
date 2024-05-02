import logging
from typing import Optional

from lettrade.data import DataFeed
from lettrade.exchange import Exchange, OrderType

from .trades import BackTestExecute, BackTestOrder, BackTestTrade

logger = logging.getLogger(__name__)


class BackTestExchange(Exchange):
    __id = 0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._init_trade_classes()

    def _init_trade_classes(self):
        BackTestOrder._trade_cls = BackTestTrade
        BackTestOrder._execute_cls = BackTestExecute

    def _id(self) -> str:
        self.__id += 1
        return str(self.__id)

    def next(self):
        self._simulate_orders()

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

        order = BackTestOrder(
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
            open_bar=self.data.index[0],
        )
        order.place()

        if __debug__:
            logger.info("New order %s at %s", order, self.data.now)

        self._simulate_orders()

    def _simulate_orders(self):
        price = self.data.open[0]
        bar = self.data.index[0]
        for order in self.orders.to_list():
            self._simulate_order(order, price, bar)

    def _simulate_order(self, order: BackTestOrder, price: float, bar: int):
        if order.type == OrderType.Market:
            order.execute(price=price, bar=bar)
            return

        elif order.type == OrderType.Limit:
            if order.is_long:
                if order.limit_price > price:
                    order.execute(price=order.limit_price, bar=bar)
                    return
            else:
                if order.limit_price < price:
                    order.execute(price=order.limit_price, bar=bar)
                    return
