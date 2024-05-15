import logging
from typing import Any, Type

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
        limit_price: float | None = None,
        stop_price: float | None = None,
        sl_price: float | None = None,
        tp_price: float | None = None,
        trade: Any | None = None,
        parent: Order | None = None,
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


class MetaTraderTrade(Trade):
    pass
