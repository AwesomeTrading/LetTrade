import logging
from typing import Optional, Type

from lettrade.data import DataFeed
from lettrade.exchange import Exchange, OrderResult, OrderType, PositionState

from .api import LiveAPI
from .trade import LiveExecution, LiveOrder, LivePosition

logger = logging.getLogger(__name__)


class LiveExchange(Exchange):
    """MetaTrade 5 exchange module for `lettrade`"""

    _execution_cls: Type[LiveExecution] = LiveExecution
    _order_cls: Type[LiveOrder] = LiveOrder
    _position_cls: Type[LivePosition] = LivePosition

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
        type: Optional[OrderType] = OrderType.Market,
        limit: Optional[float] = None,
        stop: Optional[float] = None,
        sl: Optional[float] = None,
        tp: Optional[float] = None,
        tag: Optional[str] = None,
        data: Optional[DataFeed] = None,
        *args,
        **kwargs
    ) -> OrderResult:
        """Place new order to server

        Args:
            size (float): _description_
            type (Optional[OrderType], optional): _description_. Defaults to OrderType.Market.
            limit (Optional[float], optional): _description_. Defaults to None.
            stop (Optional[float], optional): _description_. Defaults to None.
            sl (Optional[float], optional): _description_. Defaults to None.
            tp (Optional[float], optional): _description_. Defaults to None.
            tag (Optional[str], optional): _description_. Defaults to None.
            data (Optional[DataFeed], optional): _description_. Defaults to None.

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
        )
        ok = order.place()

        # if __debug__:
        #     logger.info("New order %s at %s", order, self.data.now)

        return ok

    # Events
    def on_deals_new(self, raws):
        if __debug__:
            logger.debug("Raw new deals: %s", raws)
        for raw in raws:
            execution = self._execution_cls.from_raw(raw=raw, exchange=self)
            if execution is None:
                continue
            self.on_execution(execution)

    def on_orders_new(self, raws):
        if __debug__:
            logger.debug("Raw new orders: %s", raws)
        for raw in raws:
            order = self._order_cls.from_raw(raw=raw, exchange=self)
            if order is None:
                continue
            self.on_order(order)

    def on_orders_old(self, raws):
        if __debug__:
            logger.debug("Raw old orders: %s", raws)
        for raw in raws:
            order = self._order_cls.from_raw(raw=raw, exchange=self)
            if order is None:
                continue
            self.on_order(order)

    def on_positions_new(self, raws):
        if __debug__:
            logger.debug("Raw new positions: %s", raws)
        for raw in raws:
            position = self._position_cls.from_raw(
                raw=raw,
                exchange=self,
                state=PositionState.Open,
            )
            if position is None:
                continue
            self.on_position(position)

    def on_positions_old(self, raws):
        if __debug__:
            logger.debug("Raw old positions: %s", raws)
        for raw in raws:
            position = self._position_cls.from_raw(
                raw=raw,
                exchange=self,
                state=PositionState.Exit,
            )
            if position is None:
                continue
            self.on_position(position)
