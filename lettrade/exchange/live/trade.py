import logging
from typing import Optional

from lettrade.exchange import (
    Execution,
    Order,
    OrderResult,
    OrderResultError,
    OrderResultOk,
    OrderState,
    OrderType,
    Position,
    PositionState,
    TradeSide,
)

from .api import LiveAPI

logger = logging.getLogger(__name__)


class LiveExecution(Execution):
    """
    Execution for Live
    """

    def __init__(
        self,
        id: str,
        exchange: "LiveExchange",
        data: "DataFeed",
        size: float,
        price: float,
        at: float,
        order_id: Optional[str] = None,
        order: Optional["Order"] = None,
        position_id: Optional[str] = None,
        position: Optional["Position"] = None,
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
            position_id=position_id,
            position=position,
        )
        self.tag: str = tag
        self.raw: object = raw
        self._api: LiveAPI = exchange._api

    @classmethod
    def from_raw(cls, raw, exchange: "LiveExchange") -> "LiveExecution":
        """
        Building new LiveExecution from live api deal object

            Raw deal: TradeDeal(ticket=33889131, order=41290404, time=1715837856, time_msc=1715837856798, type=0, entry=0, magic=0, position_id=41290404, reason=0, volume=0.01, price=0.85795, commission=0.0, swap=0.0, profit=0.0, fee=0.0, symbol='EURGBP', comment='', external_id='')
        """

        return cls(
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
            position_id=raw.position_id,
            tag=raw.comment,
            raw=raw,
        )


class LiveOrder(Order):
    def __init__(
        self,
        id: str,
        exchange: "LiveExchange",
        data: "DataFeed",
        size: float,
        state: OrderState = OrderState.Pending,
        type: OrderType = OrderType.Market,
        limit_price: Optional[float] = None,
        stop_price: Optional[float] = None,
        sl_price: Optional[float] = None,
        tp_price: Optional[float] = None,
        parent: Optional["Position"] = None,
        tag: Optional[str] = "",
        api: Optional[LiveAPI] = None,
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
            parent=parent,
            tag=tag,
        )
        self._api: LiveAPI = api or exchange._api

        self.raw: dict = None

    def place(self) -> "OrderResult":
        if self.state != OrderState.Pending:
            raise RuntimeError(f"Order {self.id} state {self.state} is not Pending")

        result = self._api.order_open(self)
        self.raw = result
        if result.code != 0:
            logger.error("Place order %s", str(result))
            error = OrderResultError(
                error=result.comment,
                code=result.code,
                order=self,
                raw=result,
            )
            self.exchange.on_notify(error=error)
            return error

        self.id = result.order
        # TODO: test
        ok = super().place(at=self.data.l.index[0])
        ok.raw = result
        return ok

    def update(
        self,
        limit_price: float = None,
        stop_price: float = None,
        sl: float = None,
        tp: float = None,
        **kwargs,
    ) -> "OrderResult":
        result = self._api.order_update(
            order=self,
            limit_price=limit_price,
            stop_price=stop_price,
            sl=sl,
            tp=tp,
            **kwargs,
        )
        # TODO: test
        return super().update(
            limit_price=result.limit_price,
            stop_price=result.stop_price,
            sl=result.sl,
            tp=result.tp,
        )

    def cancel(self, **kwargs) -> "OrderResult":
        self._api.order_close(order=self, **kwargs)
        # TODO: test
        return super().cancel()

    @classmethod
    def from_raw(cls, raw, exchange: "LiveExchange") -> "LiveOrder":
        return cls(
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
        )


class LivePosition(Position):
    def __init__(
        self,
        id: str,
        exchange: "LiveExchange",
        data: "DataFeed",
        size: float,
        parent: Order,
        tag: str = "",
        state: PositionState = PositionState.Open,
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
        self._api: LiveAPI = exchange._api

    @classmethod
    def from_raw(cls, raw, exchange: "LiveExchange") -> "LivePosition":
        return cls(
            exchange=exchange,
            id=raw.ticket,
            state=PositionState.Open,
            # TODO: Fix by get data from symbol
            data=exchange.data,
            # TODO: size and type from raw.type
            size=raw.volume,
            entry_price=raw.price_open,
            parent=None,
            tag=raw.comment,
        )
