import logging
from typing import Optional, Type

import pandas as pd

from .base import BaseTransaction, OrderState, OrderType
from .error import LetTradeOrderValidateException

logger = logging.getLogger(__name__)


class Order(BaseTransaction):
    _trade_cls: Type["Trade"] = None
    _execute_cls: Type["Execute"] = None

    def __init__(
        self,
        id: str,
        exchange: "Exchange",
        data: "DataFeed",
        size: float,
        state: OrderState = OrderState.Pending,
        type: OrderType = OrderType.Market,
        limit_price: Optional[float] = None,
        stop_price: Optional[float] = None,
        sl_price: Optional[float] = None,
        tp_price: Optional[float] = None,
        trade: Optional["Trade"] = None,
        tag: Optional[object] = None,
        open_at: Optional[pd.Timestamp] = None,
        open_price: Optional[float] = None,
    ):
        super().__init__(
            id=id,
            exchange=exchange,
            data=data,
            size=size,
        )

        self.type: OrderType = type
        self.state: OrderState = state
        self.limit_price: Optional[float] = limit_price
        self.stop_price: Optional[float] = stop_price
        self.sl_price: Optional[float] = sl_price
        self.tp_price: Optional[float] = tp_price
        self.trade: Optional["Trade"] = trade
        self.tag: Optional[object] = tag

        self.open_at: Optional[pd.Timestamp] = open_at
        self.open_price: Optional[float] = open_price
        self.entry_at: Optional[pd.Timestamp] = None
        self.entry_price: Optional[float] = None

        self.validate()

    def __repr__(self):
        return "<Order {}>".format(
            ", ".join(
                f"{param}={value if isinstance(value, str) else round(value, 5)}"
                for param, value in (
                    ("id", self.id),
                    ("type", self.type),
                    ("state", self.state),
                    ("size", self.size),
                    ("limit", self.limit_price),
                    ("stop", self.stop_price),
                    ("sl", self.sl_price),
                    ("tp", self.tp_price),
                    ("tag", self.tag),
                )
                if value is not None
            )
        )

    def validate(self):
        # Validate
        price = self.limit_price or self.stop_price or self.data.l.close[-1]

        # Buy side
        if self.size > 0:
            if self.sl_price is not None:
                if self.sl_price >= price:
                    raise LetTradeOrderValidateException(
                        f"Order buy sl {self.sl_price} >= price {price}"
                    )
            if self.tp_price is not None:
                if self.tp_price <= price:
                    raise LetTradeOrderValidateException(
                        f"Order buy tp {self.tp_price} >= price {price}"
                    )
        # Sell side
        elif self.size < 0:
            if self.sl_price is not None:
                if self.sl_price <= price:
                    raise LetTradeOrderValidateException(
                        f"Order sell sl {self.sl_price} <= price {price}"
                    )
            if self.tp_price is not None:
                if self.tp_price >= price:
                    raise LetTradeOrderValidateException(
                        f"Order sell tp {self.tp_price} >= price {price}"
                    )
        else:
            raise LetTradeOrderValidateException(f"Order side {self.size} is invalid")

    def _on_place(self) -> "OrderResult":
        """Place `Order`
        Set `status` to `OrderState.Placed`.
        Send event to `Exchange`

        Raises:
            RuntimeError: _description_

        Returns:
            OrderResult: result of `Order`
        """
        if self.state != OrderState.Pending:
            raise RuntimeError(f"Order {self.id} state {self.state} is not Pending")

        self.state = OrderState.Placed

        logger.info("Placing new order: %s", self)

        self.exchange.on_order(self)
        return OrderResultOk(order=self)

    def _on_execute(self, price: float, at: pd.Timestamp) -> "OrderResult":
        """Execute `Order`.
        Set `status` to `OrderState.Executed`.
        Send event to `Exchange`

        Args:
            price (float): Executed price
            at (pd.Timestamp): Executed bar

        Raises:
            RuntimeError: _description_

        Returns:
            OrderResult: result of `Order`
        """
        if self.state != OrderState.Placed:
            raise RuntimeError(f"Order {self.id} state {self.state} is not Placed")

        self.entry_at = at
        self.entry_price = price
        self.state = OrderState.Executed
        self.exchange.on_order(self)
        return OrderResultOk(order=self)

    def _on_cancel(self) -> "OrderResult":
        """Cancel `Order`
        Set `status` to `OrderState.Canceled`.
        Send event to `Exchange`

        Raises:
            RuntimeError: Validate state is `OrderState.Placed`

        Returns:
            OrderResult: result of `Order`
        """
        if self.state != OrderState.Placed:
            raise RuntimeError(f"Order {self.id} state {self.state} is not Placed")

        self.state = OrderState.Canceled
        self.exchange.on_order(self)
        return OrderResultOk(order=self)

    def update(self, sl=None, tp=None, **kwargs):
        """"""
        raise NotImplementedError

    def cancel(self):
        """"""
        raise NotImplementedError

    def merge(self, other: "Order"):
        """Update current `Order` variables by other `Order`

        Args:
            other (Order): Merge source `Order`

        Raises:
            RuntimeError: Validate same id
        """
        if other is self:
            return

        if self.id != other.id:
            raise RuntimeError(f"Merge difference id {self.id} != {other.id} order")

        self.size = other.size
        self.sl_price = other.sl_price
        self.tp_price = other.tp_price

        if other.open_price:
            self.open_price = other.open_price
        if other.open_at:
            self.open_at = other.open_at
        if other.entry_price:
            self.entry_price = other.entry_price
        if other.entry_at:
            self.entry_at = other.entry_at
        if other.trade:
            self.trade = other.trade

    # Fields getters
    @property
    def limit(self) -> Optional[float]:
        """Getter of limit_price

        Returns:
            Optional[float]: `float` or `None`
        """
        return self.limit_price

    @property
    def stop(self) -> Optional[float]:
        """Getter of stop_price

        Returns:
            Optional[float]: `float` or `None`
        """
        return self.stop_price

    @property
    def sl(self) -> Optional[float]:
        """Getter of sl_price

        Returns:
            Optional[float]: `float` or `None`
        """
        return self.sl_price

    @property
    def tp(self) -> Optional[float]:
        """Getter of tp_price

        Returns:
            Optional[float]: `float` or `None`
        """
        return self.tp_price

    # Extra properties
    @property
    def is_sl_order(self) -> bool:
        """`Order` is stop-loss order of a `Trade`

        Returns:
            bool: _description_
        """
        return self.trade and self is self.trade.sl_order

    @property
    def is_tp_order(self) -> bool:
        """`Order` is take-profit order of a `Trade`

        Returns:
            bool: _description_
        """
        return self.trade and self is self.trade.tp_order

    @property
    def is_alive(self) -> bool:
        """Flag to check `Order` still alive

        Returns:
            bool: True if `state` in [OrderState.Pending, OrderState.Placed]
        """
        return self.state in [OrderState.Pending, OrderState.Placed]


class OrderResult:
    """Result of `Order`"""

    def __init__(
        self,
        ok: bool = True,
        code: int = 0,
        order: Optional["Order"] = None,
        raw: Optional[object] = None,
    ) -> None:
        """_summary_

        Args:
            ok (Optional[bool], optional): Flag to check `Order` is success or not. Defaults to True.
            order (Optional[Order], optional): Order own the result. Defaults to None.
            code (Optional[int], optional): Error code of result. Defaults to 0.
            raw (Optional[object], optional): Raw object of `Order`. Defaults to None.
        """
        self.ok: bool = ok
        self.code: int = code
        self.order: Optional["Order"] = order
        self.raw: Optional[object] = raw


class OrderResultOk(OrderResult):
    """Result of a success `Order`"""

    def __init__(
        self,
        order: Optional["Order"] = None,
        raw: Optional[object] = None,
    ) -> None:
        """_summary_

        Args:
            order (Optional[Order], optional): Order own the result. Defaults to None.
            raw (Optional[object], optional): Raw object of `Order`. Defaults to None.
        """
        super().__init__(ok=True, order=order, raw=raw)


class OrderResultError(OrderResult):
    """Result of a error `Order`"""

    def __init__(
        self,
        error: str,
        code: int,
        order: Optional["Order"] = None,
        raw: Optional[object] = None,
    ) -> None:
        """_summary_

        Args:
            error (str): Error message
            code (int): Error code of result
            order (Optional[Order], optional): Order own the result. Defaults to None.
            raw (Optional[object], optional): Raw object of `Order`. Defaults to None.
        """
        super().__init__(ok=False, order=order, code=code, raw=raw)
        self.error: str = error
