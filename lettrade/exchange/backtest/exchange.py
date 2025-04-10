import logging
from datetime import datetime

from lettrade.data import DataFeed
from lettrade.exchange import (
    Exchange,
    LetOrderValidateException,
    OrderResult,
    OrderResultError,
    OrderState,
    OrderType,
)

from .trade import BackTestOrder

logger = logging.getLogger(__name__)


class BackTestExchange(Exchange):
    __id = 0

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        if self._config.setdefault("use_execution", False):
            self.executions = None

    def _id(self) -> str:
        self.__id += 1
        return str(self.__id)

    def next(self):
        """Execution when new data feeded"""
        self._simulate_orders()
        super().next()

    def on_execution(self, *args, **kwargs) -> None:
        if self.executions is None:
            logger.warning(
                "Execution transaction is disable, enable by flag: show_execution=True"
            )
            return

        super().on_execution(*args, **kwargs)

    def new_order(
        self,
        size: float,
        type: OrderType = OrderType.Market,
        limit: float | None = None,
        stop: float | None = None,
        sl: float | None = None,
        tp: float | None = None,
        tag: object | None = None,
        data: DataFeed | None = None,
        expiration: datetime | None = None,
        **kwargs,
    ) -> OrderResult:
        """Place new order.
        Then send order events to `Brain`

        Args:
            size (float): _description_
            type (OrderType | None, optional): _description_. Defaults to OrderType.Market.
            limit (float | None, optional): _description_. Defaults to None.
            stop (float | None, optional): _description_. Defaults to None.
            sl (float | None, optional): _description_. Defaults to None.
            tp (float | None, optional): _description_. Defaults to None.
            tag (object | None, optional): _description_. Defaults to None.
            data (DataFeed | None, optional): _description_. Defaults to None.
            **kwargs (dict | None, optional): Extra-parameters

        Returns:
            OrderResult: Result when place new `Order`
        """
        if data is None:
            data = self.data

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
            expiration=expiration,
            tag=tag,
            **kwargs,
        )
        try:
            ok = order.place(at=self.data.bar())
        except LetOrderValidateException as e:
            logger.error("Error when place order: %s %s", order, e)
            return OrderResultError(error=str(e), order=order)

        if type == OrderType.Market:
            # Simulate market order will send event before return order result
            self._simulate_orders()

        return ok

    def _simulate_orders(self):
        simulated = []
        for order in list(self.orders.values()):
            self._simulate_order_expire(order)
            self._simulate_order_fill(order)
            simulated.append(order.id)

        # Simulate new orders created by position SL/TP in this bar, and being executed in current bar
        for order in list(self.orders.values()):
            if order.id in simulated:
                continue
            # TP order may be canceled by SL order of position
            if not order.is_opening:
                continue
            self._simulate_order_fill(order)

    def _simulate_order_expire(self, order: BackTestOrder):
        if order.expiration is None:
            return
        if order.state != OrderState.Pending and not order.is_opening:
            return

        if self.now >= order.expiration:
            order.cancel()
            logger.info("Order %s expired", order.id)

    def _simulate_order_fill(self, order: BackTestOrder, index=0):
        if not order.is_opening:
            return

        if order.type == OrderType.Market:
            order.fill(
                price=self.data.l.close[index],
                at=self.data.bar(index),
            )
            return

        if order.type == OrderType.Limit:
            if order.is_long:
                # Buy Limit
                price = self.data.l.low[index]
                if order.limit_price > price:
                    return order.fill(price=order.limit_price, at=self.data.bar(index))
            else:
                # Sell Limit
                price = self.data.l.high[index]
                if order.limit_price < price:
                    return order.fill(price=order.limit_price, at=self.data.bar(index))
        elif order.type == OrderType.Stop:
            if order.is_long:
                # Buy Stop
                price = self.data.l.high[index]
                if order.stop_price < price:
                    return order.fill(price=order.stop_price, at=self.data.bar(index))
            else:
                # Sell Stop
                price = self.data.l.low[index]
                if order.stop_price > price:
                    return order.fill(price=order.stop_price, at=self.data.bar(index))
