import logging

from lettrade.data import DataFeed
from lettrade.exchange import Exchange, OrderResult, OrderType

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
        if not data:
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
            tag=tag,
        )
        ok = order.place(at=self.data.bar())

        if type == OrderType.Market:
            # Simulate market order will send event before return order result
            self._simulate_orders()

        return ok

    def _simulate_orders(self):
        for order in list(self.orders.values()):
            self._simulate_order(order)

    def _simulate_order(self, order: BackTestOrder):
        if not order.is_opening:
            return

        if order.type == OrderType.Market:
            order.fill(
                price=self.data.l.open[0],
                at=self.data.bar(),
            )
            return

        if order.type == OrderType.Limit:
            if order.is_long:
                # Buy Limit
                price = self.data.l.low[-1]
                if order.limit_price > price:
                    order.fill(price=order.limit_price, at=self.data.bar(-1))
                    return
            else:
                # Sell Limit
                price = self.data.l.high[-1]
                if order.limit_price < price:
                    order.fill(price=order.limit_price, at=self.data.bar(-1))
                    return
        elif order.type == OrderType.Stop:
            if order.is_long:
                # Buy Stop
                price = self.data.l.high[-1]
                if order.stop_price < price:
                    order.fill(price=order.stop_price, at=self.data.bar(-1))
                    return
            else:
                # Sell Stop
                price = self.data.l.low[-1]
                if order.stop_price > price:
                    order.fill(price=order.stop_price, at=self.data.bar(-1))
                    return
