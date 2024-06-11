import logging
from typing import Optional

from lettrade.data import DataFeed
from lettrade.exchange import Exchange, OrderResult, OrderType

from .trade import BackTestOrder

logger = logging.getLogger(__name__)


class BackTestExchange(Exchange):
    __id = 0

    def _id(self) -> str:
        self.__id += 1
        return str(self.__id)

    def next(self):
        """Execute when new data feeded"""
        self._simulate_orders()
        super().next()

    def new_order(
        self,
        size: float,
        type: Optional[OrderType] = OrderType.Market,
        limit: Optional[float] = None,
        stop: Optional[float] = None,
        sl: Optional[float] = None,
        tp: Optional[float] = None,
        tag: Optional[object] = None,
        data: Optional[DataFeed] = None,
        **kwargs
    ) -> OrderResult:
        """Place new order.
        Then send order events to `Brain`

        Args:
            size (float): _description_
            type (Optional[OrderType], optional): _description_. Defaults to OrderType.Market.
            limit (Optional[float], optional): _description_. Defaults to None.
            stop (Optional[float], optional): _description_. Defaults to None.
            sl (Optional[float], optional): _description_. Defaults to None.
            tp (Optional[float], optional): _description_. Defaults to None.
            tag (Optional[object], optional): _description_. Defaults to None.
            data (Optional[DataFeed], optional): _description_. Defaults to None.
            **kwargs (Optional[dict], optional): Extra-parameters

        Returns:
            OrderResult: Result when place new `Order`
        """
        if not data:
            data = self.data

        if type == OrderType.Market:
            limit = None
            stop = None
            open_price = self.data.l.open[0]
            open_at = self.data.bar()
        else:
            open_price = None
            open_at = None

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
            open_price=open_price,
            open_at=open_at,
        )
        ok = order._on_place()

        if __debug__:
            logger.info("New order %s at %s", order, self.data.now)

        if type == OrderType.Market:
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
            order._on_execute(
                price=self.data.l.open[0],
                at=self.data.bar(),
            )
            return

        if order.type == OrderType.Limit:
            if order.is_long:
                # Buy Limit
                price = self.data.l.low[-1]
                if order.limit_price > price:
                    order._on_execute(price=order.limit_price, at=self.data.bar(-1))
                    return
            else:
                # Sell Limit
                price = self.data.l.high[-1]
                if order.limit_price < price:
                    order._on_execute(price=order.limit_price, at=self.data.bar(-1))
                    return
        elif order.type == OrderType.Stop:
            if order.is_long:
                # Buy Stop
                price = self.data.l.high[-1]
                if order.stop_price < price:
                    order._on_execute(price=order.stop_price, at=self.data.bar(-1))
                    return
            else:
                # Sell Stop
                price = self.data.l.low[-1]
                if order.stop_price > price:
                    order._on_execute(price=order.stop_price, at=self.data.bar(-1))
                    return
