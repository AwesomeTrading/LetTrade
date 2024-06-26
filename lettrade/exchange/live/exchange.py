import logging

from lettrade.data import DataFeed
from lettrade.exchange import Exchange, OrderResult, OrderType, PositionState

from .api import LiveAPI
from .trade import LiveExecution, LiveOrder, LivePosition

logger = logging.getLogger(__name__)


class LiveExchange(Exchange):
    """MetaTrade 5 exchange module for `lettrade`"""

    _execution_cls: type[LiveExecution] = LiveExecution
    _order_cls: type[LiveOrder] = LiveOrder
    _position_cls: type[LivePosition] = LivePosition

    _api: LiveAPI

    def __init__(self, api: LiveAPI, *args, **kwargs):
        """_summary_

        Args:
            api (LiveAPI): API connect to rpyc MeTrader 5 Terminal server through module `mt5linux`
            *args (list): `Exchange` list parameters
            **kwargs (dict): `Exchange` dict parameters
        """
        super().__init__(*args, **kwargs)
        self._api = api

    def start(self) -> None:
        """Start Live exchange by: Sync positions from server"""
        self._api.start(exchange=self)
        return super().start()

    def next(self) -> None:
        self._api.next()
        return super().next()

    def new_order(
        self,
        size: float,
        type: OrderType | None = OrderType.Market,
        limit: float | None = None,
        stop: float | None = None,
        sl: float | None = None,
        tp: float | None = None,
        tag: str | None = None,
        data: DataFeed | None = None,
        **kwargs,
    ) -> OrderResult:
        """Place new order to server

        Args:
            size (float): _description_
            type (OrderType | None, optional): _description_. Defaults to OrderType.Market.
            limit (float | None, optional): _description_. Defaults to None.
            stop (float | None, optional): _description_. Defaults to None.
            sl (float | None, optional): _description_. Defaults to None.
            tp (float | None, optional): _description_. Defaults to None.
            tag (str | None, optional): _description_. Defaults to None.
            data (DataFeed | None, optional): _description_. Defaults to None.

        Returns:
            OrderResult: _description_
        """
        if not data:
            data = self.data

        if type == OrderType.Market:
            limit = 0
            stop = 0

        order = self._order_cls(
            id=-1,
            exchange=self,
            data=data,
            size=size,
            type=type,
            limit_price=limit,
            stop_price=stop,
            sl_price=sl,
            tp_price=tp,
            tag=tag,
            **kwargs,
        )
        ok = order.place()

        # if __debug__:
        #     logger.info("New order %s at %s", order, self.data.now)

        return ok

    # Events
    def on_executions_event(self, raws, broadcast: bool | None = True):
        if __debug__:
            logger.debug("Raw new executions: %s", raws)
        for raw in raws:
            execution = self._execution_cls.from_raw(raw=raw, exchange=self)
            if execution is None:
                continue
            self.on_execution(execution, broadcast=broadcast)

    def on_orders_event(self, new: list = None, old: list = None):
        if __debug__:
            logger.debug("Raw orders new: %s, old: %s", new, old)

        if new is None:
            new = []
        if old is None:
            old = []

        orders = []
        for raw in [*new, *old]:
            order = self._order_cls.from_raw(raw=raw, exchange=self)
            if order is None:
                continue
            orders.append(order)

        if orders:
            self.on_orders(orders)

    def on_positions_event(self, new: list = None, old: list = None):
        if __debug__:
            logger.debug("Raw positions new: %s, old: %s", new, old)

        # Positions new
        positions_new = []
        if new:
            for raw in new:
                position = self._position_cls.from_raw(
                    raw=raw,
                    exchange=self,
                    state=PositionState.Open,
                )
                if position is None:
                    continue
                positions_new.append(position)

        # positions_old
        positions_old = []
        if old:
            for raw in old:
                position = self._position_cls.from_raw(
                    raw=raw,
                    exchange=self,
                    state=PositionState.Exit,
                )
                if position is None:
                    continue
                positions_old.append(position)

        # Event
        positions = [*positions_new, *positions_old]
        if positions:
            self.on_positions(positions)
