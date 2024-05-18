import logging
from typing import Optional

from lettrade.data import DataFeed
from lettrade.exchange import Exchange, OrderType

logger = logging.getLogger(__name__)

from .api import MetaTraderAPI
from .trade import MetaTraderExecute, MetaTraderOrder, MetaTraderTrade


class MetaTraderExchange(Exchange):
    _api: MetaTraderAPI

    def __init__(self, api: MetaTraderAPI, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._api = api
        self._api._callbacker = self

    def start(self):
        self._sync_orders()
        self._sync_trades()
        return super().start()

    def next(self):
        self._api._check_transactions()
        super().next()

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
    ):
        if not data:
            data = self.data

        if type == OrderType.Market:
            limit = 0
            stop = 0

        order = MetaTraderOrder(
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
            open_price=self.data.open[0],
            open_at=self.data.bar(),
        )
        ok = order.place()

        if __debug__:
            logger.info("New order %s at %s", order, self.data.now)

        return ok

    def _sync_orders(self):
        total = self._api.orders_total()
        if total <= 0:
            return

        raws = self._api.orders_get()
        if not raws:
            logger.warning("Cannot get orders")
            return

        for order in self._parse_orders(raws):
            if __debug__:
                logger.info("Sync order: %s", order)
            self.on_order(order)

    def _parse_orders(self, raws) -> list[MetaTraderOrder]:
        return [self._parse_order(raw) for raw in raws]

    def _parse_order(self, raw) -> MetaTraderOrder:
        return MetaTraderOrder.from_raw(raw=raw, exchange=self)

    def _sync_trades(self):
        total = self._api.positions_total()
        if total <= 0:
            return

        raws = self._api.positions_get()
        if not raws:
            logger.warning("Cannot get trades")
            return

        for raw in raws:
            if __debug__:
                logger.info("Sync trade: %s", raw)
            if raw.ticket not in self.trades:
                trade = MetaTraderTrade.from_raw(raw=raw, exchange=self)
                self.on_trade(trade)

    # Events
    def on_new_deals(self, raws):
        if __debug__:
            logger.info("Raw new deals: %s", raws)
        for raw in raws:
            execute = MetaTraderExecute.from_raw(raw, exchange=self)
            self.on_execute(execute)

    def on_new_orders(self, raws):
        if __debug__:
            logger.info("Raw new orders: %s", raws)
        for raw in raws:
            order = MetaTraderOrder.from_raw(raw, exchange=self)
            self.on_order(order)

    def on_old_orders(self, raws):
        if __debug__:
            logger.info("Raw old orders: %s", raws)
        for raw in raws:
            order = MetaTraderOrder.from_raw(raw, exchange=self)
            self.on_order(order)

    def on_new_trades(self, raws):
        if __debug__:
            logger.info("Raw new trades: %s", raws)
        for raw in raws:
            trade = MetaTraderTrade.from_raw(raw, exchange=self)
            self.on_trade(trade)

    def on_old_trades(self, raws):
        if __debug__:
            logger.info("Raw old trades: %s", raws)
        for raw in raws:
            trade = MetaTraderTrade.from_raw(raw, exchange=self)
            self.on_trade(trade)
