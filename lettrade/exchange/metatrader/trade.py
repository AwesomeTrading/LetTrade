import logging
from typing import Any, Optional, Type

from mt5linux import MetaTrader5 as mt5

from .. import (
    Execute,
    Order,
    OrderResult,
    OrderResultError,
    OrderResultOk,
    OrderState,
    OrderType,
    Trade,
    TradeState,
)
from .api import MetaTraderAPI

logger = logging.getLogger(__name__)


class MetaTraderExecute(Execute):
    """
    Execute for MetaTrader
    """


class MetaTraderOrder(Order):
    _api: MetaTraderAPI

    def __init__(
        self,
        id: str,
        exchange: "Exchange",
        api: MetaTraderAPI,
        data: "DataFeed",
        size: float,
        state: OrderState = OrderState.Pending,
        type: OrderType = OrderType.Market,
        limit_price: Optional[float] = None,
        stop_price: Optional[float] = None,
        sl_price: Optional[float] = None,
        tp_price: Optional[float] = None,
        trade: Optional["Trade"] = None,
        parent: Optional[Order] = None,
        tag: object = None,
        open_bar: int = None,
        open_price: int = None,
    ):
        super().__init__(
            id,
            exchange,
            data,
            size,
            state,
            type,
            limit_price,
            stop_price,
            sl_price,
            tp_price,
            trade,
            parent,
            tag,
            open_bar,
            open_price,
        )
        self._api = api

    def place(self):
        if self.state != OrderState.Pending:
            raise RuntimeError(f"Order {self.id} state {self.state} is not Pending")

        request = self._build_request()
        result = self._api.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            logger.error("Place order %s", str(result))
            error = OrderResultError(
                error=result.comment,
                code=result.retcode,
                order=self,
                raw=result,
            )
            self.exchange.on_notify(error=error)
            return error

        self.id = result.order
        ok = super().place()
        ok.raw = result
        return ok

    def _build_request(self):
        price = self._api.tick(self.data.symbol).ask
        deviation = 20
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.data.symbol,
            "volume": self.size,
            "type": mt5.ORDER_TYPE_BUY,
            "price": price,
            "sl": self.sl,
            "tp": self.tp,
            "deviation": deviation,
            "magic": 234000,
            "comment": "python script open",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        return request

    @classmethod
    def _from_raw(
        cls, raw, exchange: "Exchange", api: "MetaTraderAPI"
    ) -> "MetaTraderOrder":
        return MetaTraderOrder(
            exchange=exchange,
            api=api,
            id=raw.ticket,
            state=OrderState.Place,
            # TODO: Fix by get data from symbol
            data=exchange.data,
            # TODO: size and type from raw.type
            size=raw.volume_current,
            type=OrderType.Market,
            limit_price=raw.price_open,
            stop_price=raw.price_open,
            sl_price=raw.sl,
            tp_price=raw.tp,
            tag=raw.comment,
            open_price=raw.price_open,
            open_bar=raw.price_open,
        )


class MetaTraderTrade(Trade):
    _api: MetaTraderAPI

    def __init__(
        self,
        id: str,
        exchange: "Exchange",
        api: MetaTraderAPI,
        data: "DataFeed",
        size: float,
        parent: Order,
        tag: object = "",
        state: TradeState = TradeState.Open,
        entry_price: float | None = None,
        entry_bar: int | None = None,
        sl_order: Order | None = None,
        tp_order: Order | None = None,
    ):
        super().__init__(
            id,
            exchange,
            data,
            size,
            parent,
            tag,
            state,
            entry_price,
            entry_bar,
            sl_order,
            tp_order,
        )
        self._api = api

    @classmethod
    def _from_raw(
        cls, raw, exchange: "Exchange", api: "MetaTraderAPI"
    ) -> "MetaTraderTrade":
        return MetaTraderTrade(
            exchange=exchange,
            api=api,
            id=raw.ticket,
            state=TradeState.Open,
            # TODO: Fix by get data from symbol
            data=exchange.data,
            # TODO: size and type from raw.type
            size=raw.volume,
            entry_price=raw.price_open,
            parent=None,
            tag=raw.comment,
        )
