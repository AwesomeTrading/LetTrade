import logging
from abc import ABCMeta, abstractmethod
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
    PositionResultError,
    PositionResultOk,
    PositionState,
)

from .api import LiveAPI

logger = logging.getLogger(__name__)


class _LiveTrade:
    def __init__(
        self,
        exchange: "LiveExchange",
        api: Optional[LiveAPI] = None,
        raw: Optional[object] = None,
        **kwargs,
    ) -> None:
        super().__init__(exchange=exchange, **kwargs)
        self.raw: object = raw
        self._api: LiveAPI = api or exchange._api


class LiveExecution(_LiveTrade, Execution, metaclass=ABCMeta):
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
        # tag: Optional[str] = "",
        api: Optional[LiveAPI] = None,
        raw: Optional[object] = None,
        **kwargs,
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
            api=api,
            raw=raw,
            **kwargs,
        )
        # self.tag: str = tag
        # self.raw: object = raw
        # self._api: LiveAPI = api or exchange._api

    @classmethod
    def from_raw(cls, raw, exchange: "LiveExchange") -> "LiveExecution":
        """Building new LiveExecution from live api raw object

        Args:
            raw (_type_): _description_
            exchange (LiveExchange): _description_

        Returns:
            LiveExecution: _description_
        """
        raise NotImplementedError


class LiveOrder(_LiveTrade, Order, metaclass=ABCMeta):
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
        raw: Optional[object] = None,
        **kwargs,
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
            api=api,
            raw=raw,
            **kwargs,
        )
        # self.raw: dict = raw
        # self._api: LiveAPI = api or exchange._api

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
        # TODO: get current order time
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
    @abstractmethod
    def from_raw(cls, raw, exchange: "LiveExchange") -> "LiveOrder":
        """_summary_

        Args:
            raw (_type_): _description_
            exchange (LiveExchange): _description_

        Returns:
            LiveOrder: _description_
        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def from_position(cls, position: "LivePosition", sl=None, tp=None) -> "LiveOrder":
        """_summary_

        Args:
            position (LivePosition): _description_
            sl (_type_, optional): _description_. Defaults to None.
            tp (_type_, optional): _description_. Defaults to None.

        Returns:
            LiveOrder: _description_
        """
        raise NotImplementedError


class LivePosition(_LiveTrade, Position, metaclass=ABCMeta):
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
        api: Optional[LiveAPI] = None,
        raw: Optional[object] = None,
        **kwargs,
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
            api=api,
            raw=raw,
            **kwargs,
        )
        # self.raw: dict = raw
        # self._api: LiveAPI = api or exchange._api

    def update(self, sl: float = None, tp: float = None, **kwargs):
        if not sl and not tp:
            raise RuntimeError("Update sl=None and tp=None")

        result = self._api.position_update(position=self, sl=sl, tp=tp)
        if result.code != 0:
            logger.error("Update position %s", str(result))
            error = PositionResultError(
                error=result.comment,
                code=result.code,
                position=self,
                raw=result,
            )
            self.exchange.on_notify(error=error)
            return error

        if sl is not None:
            if self.sl_order:
                self.sl_order.update(stop_price=sl)
            else:
                self.sl_order = self.exchange._order_cls.from_position(
                    position=self, sl=sl
                )

        if tp is not None:
            if self.tp_order:
                self.tp_order.update(limit_price=tp)
            else:
                self.tp_order = self.exchange._order_cls.from_position(
                    position=self, tp=tp
                )

        self.exchange.on_position(self)

    @classmethod
    @abstractmethod
    def from_raw(cls, raw, exchange: "LiveExchange") -> "LivePosition":
        """_summary_

        Args:
            raw (_type_): _description_
            exchange (LiveExchange): _description_

        Returns:
            LivePosition: _description_
        """
        raise NotImplementedError

    # @classmethod
    # # @abstractmethod
    # def from_id(cls, id: str, exchange: "LiveExchange") -> "LivePosition":
    #     """_summary_

    #     Args:
    #         id (str): _description_
    #         exchange (LiveExchange): _description_

    #     Returns:
    #         LivePosition: _description_
    #     """
    #     raise NotImplementedError
