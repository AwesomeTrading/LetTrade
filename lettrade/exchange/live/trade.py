import logging
from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING

from lettrade.exchange import (
    Execution,
    Order,
    OrderResult,
    OrderState,
    OrderType,
    Position,
    PositionResult,
    PositionState,
)

from .api import LiveAPI

if TYPE_CHECKING:
    from .data import LiveDataFeed
    from .exchange import LiveExchange

logger = logging.getLogger(__name__)


class _LiveTrade:
    def __init__(
        self,
        exchange: "LiveExchange",
        api: LiveAPI | None = None,
        raw: object | None = None,
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
        data: "LiveDataFeed",
        size: float,
        price: float,
        at: float,
        order_id: str | None = None,
        order: "Order | None" = None,
        position_id: str | None = None,
        position: "Position | None" = None,
        # tag: str | None = None,
        api: LiveAPI | None = None,
        raw: object | None = None,
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
        # self.tag: str | None = tag

    @classmethod
    @abstractmethod
    def from_raw(cls, raw, exchange: "LiveExchange") -> "LiveExecution":
        """Building new LiveExecution from live api raw object

        Args:
            raw (_type_): _description_
            exchange (LiveExchange): _description_

        Returns:
            LiveExecution: _description_
        """
        raise NotImplementedError(cls)


class LiveOrder(_LiveTrade, Order, metaclass=ABCMeta):
    def __init__(
        self,
        id: str,
        exchange: "LiveExchange",
        data: "LiveDataFeed",
        size: float,
        state: OrderState = OrderState.Pending,
        type: OrderType = OrderType.Market,
        limit_price: float | None = None,
        stop_price: float | None = None,
        sl_price: float | None = None,
        tp_price: float | None = None,
        parent: "Position | None" = None,
        tag: str | None = None,
        api: LiveAPI | None = None,
        raw: object | None = None,
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

    @abstractmethod
    def place(self) -> OrderResult:
        raise NotImplementedError(type(self))

        # if self.state != OrderState.Pending:
        #     raise RuntimeError(f"Order {self.id} state {self.state} is not Pending")

        # result = self._api.order_open(self)
        # self.raw = result
        # if result.code != 0:
        #     logger.error("Place order %s", str(result))
        #     error = OrderResultError(
        #         error=result.error,
        #         code=result.code,
        #         order=self,
        #         raw=result,
        #     )
        #     self.exchange.on_notify(error=error)
        #     return error

        # self.id = result.order
        # # TODO: get current order time
        # return super().place(at=self.data.l.index[0], raw=result)

    @abstractmethod
    def update(
        self,
        limit_price: float | None = None,
        stop_price: float | None = None,
        sl: float | None = None,
        tp: float | None = None,
        caller: float | None = None,
        **kwargs,
    ) -> OrderResult:
        raise NotImplementedError(type(self))
        # if caller is self:
        #     raise RuntimeError(f"Order recusive update {self}")

        # result = self._api.order_update(
        #     order=self,
        #     limit_price=limit_price,
        #     stop_price=stop_price,
        #     sl=sl,
        #     tp=tp,
        #     **kwargs,
        # )

        # return super().update(
        #     limit_price=result.limit_price,
        #     stop_price=result.stop_price,
        #     sl=result.sl,
        #     tp=result.tp,
        # )

    def cancel(self, **kwargs) -> OrderResult:
        """Cancel order

        Returns:
            OrderResult: _description_
        """
        result = self._api.order_close(order=self, **kwargs)
        return super().cancel(raw=result)

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
        raise NotImplementedError(cls)

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
        raise NotImplementedError(cls)


class LivePosition(_LiveTrade, Position, metaclass=ABCMeta):
    def __init__(
        self,
        id: str,
        exchange: "LiveExchange",
        data: "LiveDataFeed",
        size: float,
        parent: Order,
        tag: str | None = None,
        state: PositionState = PositionState.Open,
        entry_price: float | None = None,
        entry_fee: float = 0.0,
        entry_at: int | None = None,
        sl_order: Order | None = None,
        tp_order: Order | None = None,
        api: LiveAPI | None = None,
        raw: object | None = None,
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
            entry_fee=entry_fee,
            entry_at=entry_at,
            sl_order=sl_order,
            tp_order=tp_order,
            api=api,
            raw=raw,
            **kwargs,
        )

    @abstractmethod
    def update(
        self,
        sl: float | None = None,
        tp: float | None = None,
        caller: float | None = None,
        **kwargs,
    ) -> PositionResult:
        """_summary_

        Args:
            sl (float | None, optional): _description_. Defaults to None.
            tp (float | None, optional): _description_. Defaults to None.
            caller (float | None, optional): _description_. Defaults to None.

        Raises:
            NotImplementedError: _description_
        """
        raise NotImplementedError(type(self))

    @abstractmethod
    def exit(self) -> PositionResult:
        """_summary_

        Returns:
            bool: _description_
        """
        raise NotImplementedError(type(self))

    def merge(self, other: "LivePosition") -> bool:
        """Merge LivePosition from another

        Args:
            other (LivePosition): _description_

        Returns:
            bool: _description_
        """
        if not super().merge(other):
            return False
        self.raw = other.raw
        return True

    @classmethod
    @abstractmethod
    def from_raw(
        cls,
        raw,
        exchange: "LiveExchange",
        state: PositionState = PositionState.Open,
        **kwargs,
    ) -> "LivePosition":
        """_summary_

        Args:
            raw (_type_): _description_
            exchange (LiveExchange): _description_

        Returns:
            LivePosition: _description_
        """
        raise NotImplementedError(cls)

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
