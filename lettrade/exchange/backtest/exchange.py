import logging
from typing import Optional

from lettrade.data import DataFeed
from lettrade.exchange import Exchange, OrderType

from .trade import BackTestExecute, BackTestOrder, BackTestTrade

logger = logging.getLogger(__name__)


class BackTestExchange(Exchange):
    __id = 0

    def _id(self) -> str:
        self.__id += 1
        return str(self.__id)

    def next(self):
        self._simulate_orders()
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
            open_at=self.data.bar(),
        )
        ok = order.place()

        if __debug__:
            logger.info("New order %s at %s", order, self.data.now)

        # Simulate market order will send event before return order result
        self._simulate_orders()

        return ok

    def _simulate_orders(self):
        for order in list(self.orders.values()):
            self._simulate_order(order)

    def _simulate_order(self, order: BackTestOrder):
        if not order.is_alive:
            return

        if order.type == OrderType.Market:
            order.execute(
                price=self.data.open[0],
                at=self.data.bar(),
            )
            return

        if order.type == OrderType.Limit:
            if order.is_long:
                # Buy Limit
                price = self.data.low[-1]
                if order.limit_price > price:
                    order.execute(price=order.limit_price, at=self.data.bar(-1))
                    return
            else:
                # Sell Limit
                price = self.data.high[-1]
                if order.limit_price < price:
                    order.execute(price=order.limit_price, at=self.data.bar(-1))
                    return
        elif order.type == OrderType.Stop:
            if order.is_long:
                # Buy Stop
                price = self.data.high[-1]
                if order.stop_price < price:
                    order.execute(price=order.stop_price, at=self.data.bar(-1))
                    return
            else:
                # Sell Stop
                price = self.data.low[-1]
                if order.stop_price > price:
                    order.execute(price=order.stop_price, at=self.data.bar(-1))
                    return
