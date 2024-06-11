import logging
from typing import Optional

from lettrade.data import DataFeed
from lettrade.exchange import Exchange, OrderResult, OrderType

from .api import LiveAPI
from .trade import LiveExecute, LiveOrder, LiveTrade

logger = logging.getLogger(__name__)


class LiveExchange(Exchange):
    """MetaTrade 5 exchange module for `lettrade`"""

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
        """Start Live exchange by: Sync orders from server, Sync trades from server"""
        self._api.start(callbacker=self)
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

        order = LiveOrder(
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
            open_price=self.data.l.open[0],
            open_at=self.data.bar(),
        )
        ok = order._place()

        if __debug__:
            logger.info("New order %s at %s", order, self.data.now)

        return ok

    # Events
    def on_new_deals(self, raws):
        if __debug__:
            logger.info("Raw new deals: %s", raws)
        for raw in raws:
            execute = LiveExecute.from_raw(raw, exchange=self)
            self.on_execute(execute)

    def on_new_orders(self, raws):
        if __debug__:
            logger.info("Raw new orders: %s", raws)
        for raw in raws:
            order = LiveOrder.from_raw(raw, exchange=self)
            self.on_order(order)

    def on_old_orders(self, raws):
        if __debug__:
            logger.info("Raw old orders: %s", raws)
        for raw in raws:
            order = LiveOrder.from_raw(raw, exchange=self)
            self.on_order(order)

    def on_new_trades(self, raws):
        if __debug__:
            logger.info("Raw new trades: %s", raws)
        for raw in raws:
            trade = LiveTrade.from_raw(raw, exchange=self)
            self.on_trade(trade)

    def on_old_trades(self, raws):
        if __debug__:
            logger.info("Raw old trades: %s", raws)
        for raw in raws:
            trade = LiveTrade.from_raw(raw, exchange=self)
            self.on_trade(trade)
