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

    def __init__(
        self,
        id: str,
        exchange: "MetaTraderExchange",
        data: "DataFeed",
        size: float,
        price: float,
        at: float,
        order_id: Optional[str] = None,
        order: Optional["Order"] = None,
        trade_id: Optional[str] = None,
        trade: Optional["Trade"] = None,
        tag: Optional[str] = "",
        raw: Optional[object] = None,
    ):
        super().__init__(
            id=id,
            exchange=exchange,
            data=data,
            size=size,
            price=price,
            at=at,
            order_id=order_id,
            order=order,
            trade_id=trade_id,
            trade=trade,
        )
        self.tag: str = tag
        self.raw: object = raw
        self._api: MetaTraderAPI = exchange._api

    # def _update_by_raw(self, raw):
    #     if self.id != raw.ticket:
    #         raise RuntimeError(f"Wrong raw execute {raw}")

    #     self.size = raw.volume
    #     self.price = raw.price

    @classmethod
    def from_raw(cls, raw, exchange: "MetaTraderExchange") -> "MetaTraderExecute":
        """
        Building new MetaTraderExecute from metatrader api deal object

            Raw deal: TradeDeal(ticket=33889131, order=41290404, time=1715837856, time_msc=1715837856798, type=0, entry=0, magic=0, position_id=41290404, reason=0, volume=0.01, price=0.85795, commission=0.0, swap=0.0, profit=0.0, fee=0.0, symbol='EURGBP', comment='', external_id='')
        """
        return MetaTraderExecute(
            exchange=exchange,
            id=raw.ticket,
            # TODO: Fix by get data from symbol
            data=exchange.data,
            # TODO: size and type from raw.type
            size=raw.volume,
            price=raw.price,
            # TODO: set bar time
            at=None,
            order_id=raw.order,
            trade_id=raw.position_id,
            tag=raw.comment,
            raw=raw,
        )


class MetaTraderOrder(Order):
    def __init__(
        self,
        id: str,
        exchange: "MetaTraderExchange",
        data: "DataFeed",
        size: float,
        state: OrderState = OrderState.Pending,
        type: OrderType = OrderType.Market,
        limit_price: Optional[float] = None,
        stop_price: Optional[float] = None,
        sl_price: Optional[float] = None,
        tp_price: Optional[float] = None,
        trade: Optional["Trade"] = None,
        tag: Optional[str] = "",
        open_at: Optional[int] = None,
        open_price: Optional[int] = None,
    ):
        super().__init__(
            id=id,
            exchange=exchange,
            data=data,
            size=size,
            state=state,
            type=type,
            limit_price=limit_price,
            stop_price=stop_price,
            sl_price=sl_price,
            tp_price=tp_price,
            trade=trade,
            tag=tag,
            open_at=open_at,
            open_price=open_price,
        )
        self._api: MetaTraderAPI = exchange._api

        self.raw = None

    def place(self):
        if self.state != OrderState.Pending:
            raise RuntimeError(f"Order {self.id} state {self.state} is not Pending")

        request = self._build_request()
        result = self._api.order_send(request)

        self.raw = result

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
        tick = self._api.tick(self.data.symbol)
        price = tick.ask if self.is_long else tick.bid
        type = mt5.ORDER_TYPE_BUY if self.is_long else mt5.ORDER_TYPE_SELL
        deviation = 20
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.data.symbol,
            "volume": self.size,
            "type": type,
            "price": price,
            "sl": self.sl,
            "tp": self.tp,
            "deviation": deviation,
            "magic": 234000,
            "comment": self.tag,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        return request

    @classmethod
    def from_raw(cls, raw, exchange: "MetaTraderExchange") -> "MetaTraderOrder":
        return MetaTraderOrder(
            exchange=exchange,
            id=raw.ticket,
            state=OrderState.Placed,
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
            open_at=raw.price_open,
        )


class MetaTraderTrade(Trade):
    def __init__(
        self,
        id: str,
        exchange: "MetaTraderExchange",
        data: "DataFeed",
        size: float,
        parent: Order,
        tag: str = "",
        state: TradeState = TradeState.Open,
        entry_price: Optional[float] = None,
        entry_at: Optional[int] = None,
        sl_order: Optional[Order] = None,
        tp_order: Optional[Order] = None,
    ):
        super().__init__(
            id=id,
            exchange=exchange,
            data=data,
            size=size,
            parent=parent,
            tag=tag,
            state=state,
            entry_price=entry_price,
            entry_at=entry_at,
            sl_order=sl_order,
            tp_order=tp_order,
        )
        self._api: MetaTraderAPI = exchange._api

    @classmethod
    def from_raw(cls, raw, exchange: "MetaTraderExchange") -> "MetaTraderTrade":
        return MetaTraderTrade(
            exchange=exchange,
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
