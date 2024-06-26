import logging
from typing import TYPE_CHECKING

import pandas as pd

from .base import BaseTransaction, OrderState, OrderType
from .error import LetOrderValidateException

if TYPE_CHECKING:
    from lettrade import DataFeed, Exchange, Position

logger = logging.getLogger(__name__)


class Order(BaseTransaction):
    def __init__(
        self,
        id: str,
        exchange: "Exchange",
        data: "DataFeed",
        size: float,
        state: OrderState = OrderState.Pending,
        type: OrderType = OrderType.Market,
        limit_price: float | None = None,
        stop_price: float | None = None,
        sl_price: float | None = None,
        tp_price: float | None = None,
        parent: "Position | None" = None,
        tag: str | None = None,
        placed_at: pd.Timestamp | None = None,
        **kwargs,
    ):
        super().__init__(
            id=id,
            exchange=exchange,
            data=data,
            size=size,
            **kwargs,
        )

        self.type: OrderType = type
        self.state: OrderState = state
        self.limit_price: float | None = limit_price
        self.stop_price: float | None = stop_price
        self.sl_price: float | None = sl_price
        self.tp_price: float | None = tp_price
        self.parent: "Position | None" = parent
        self.tag: str | None = tag
        self.placed_at: pd.Timestamp | None = placed_at
        self.filled_at: pd.Timestamp | None = None
        self.filled_price: float | None = None

    def _repr_params(self):
        params = (
            f"id='{self.id}'"
            f", type='{self.type}'"
            f", state='{self.state}'"
            f", placed_at={self.placed_at}"
            # f", place_price={round(self.place_price, 5)}"
            f", size={round(self.size, 5)}"
        )
        if self.limit:
            params += f", limit={round(self.limit, 5)}"
        if self.stop:
            params += f", stop={round(self.stop, 5)}"
        if self.sl:
            params += f", sl={round(self.sl, 5)}"
        if self.tp:
            params += f", tp={round(self.tp, 5)}"

        if self.filled_at:
            params += (
                f", filled_at={self.filled_at}" f", filled_price={self.filled_price}"
            )
        if self.tag:
            params += f", tag='{self.tag}'"

        return params

    def __repr__(self):
        return f"<{self.__class__.__name__} {self._repr_params()}>"

    def validate(self):
        # Validate
        price = self.place_price or self.data.l.open[0]

        # Buy side
        if self.size > 0:
            if self.sl_price is not None:
                if self.sl_price >= price:
                    raise LetOrderValidateException(
                        f"Order {self.id} BUY sl {self.sl_price} >= price {price}"
                    )
            if self.tp_price is not None:
                if self.tp_price <= price:
                    raise LetOrderValidateException(
                        f"Order {self.id} BUY tp {self.tp_price} <= price {price}"
                    )
        # Sell side
        elif self.size < 0:
            if self.sl_price is not None:
                if self.sl_price <= price:
                    raise LetOrderValidateException(
                        f"Order {self.id} SELL sl {self.sl_price} <= price {price}"
                    )
            if self.tp_price is not None:
                if self.tp_price >= price:
                    raise LetOrderValidateException(
                        f"Order {self.id} SELL tp {self.tp_price} >= price {price}"
                    )
        else:
            raise LetOrderValidateException(
                f"Order {self.id} side {self.size} is invalid"
            )

    def place(
        self,
        at: pd.Timestamp,
        raw: object | None = None,
    ) -> "OrderResult":
        """Place `Order`
        Set `status` to `OrderState.Placed`.
        Send event to `Exchange`

        Raises:
            RuntimeError: _description_

        Returns:
            OrderResult: result of `Order`
        """
        self.validate()

        if self.state != OrderState.Pending:
            raise RuntimeError(f"Order {self.id} state {self.state} is not Pending")

        self.state = OrderState.Placed
        self.placed_at = at

        logger.info("Placing new order: %s", self)

        self.exchange.on_order(self)
        return OrderResultOk(order=self, raw=raw)

    def update(
        self,
        limit_price: float | None = None,
        stop_price: float | None = None,
        sl: float | None = None,
        tp: float | None = None,
        raw: object | None = None,
    ) -> "OrderResult":
        """Update Order

        Args:
            limit_price (float, optional): _description_. Defaults to None.
            stop_price (float, optional): _description_. Defaults to None.
            sl (float, optional): _description_. Defaults to None.
            tp (float, optional): _description_. Defaults to None.

        Raises:
            RuntimeError: _description_
        """
        if self.is_closed:
            raise RuntimeError(f"Update a closed order {self}")

        # TODO: validate parameters
        if limit_price is not None:
            self.limit_price = limit_price
        if stop_price is not None:
            self.stop_price = stop_price

        if sl is not None:
            self.sl_price = sl
        if tp is not None:
            self.tp_price = tp

        self.exchange.on_order(self)
        return OrderResultOk(order=self, raw=raw)

    def fill(
        self,
        price: float,
        at: pd.Timestamp,
        raw: object | None = None,
    ) -> "OrderResult":
        """Fill `Order`.
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

        self.filled_at = at
        self.filled_price = price
        self.state = OrderState.Filled
        self.exchange.on_order(self)
        return OrderResultOk(order=self, raw=raw)

    def cancel(self, raw: object | None = None, **kwargs) -> "OrderResult":
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
        return OrderResultOk(order=self, raw=raw)

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

        if other.limit_price:
            self.limit_price = other.limit_price
        if other.stop_price:
            self.stop_price = other.stop_price
        if other.placed_at:
            self.placed_at = other.placed_at

        if other.filled_price:
            self.filled_price = other.filled_price
        if other.filled_at:
            self.filled_at = other.filled_at

        if other.parent:
            self.parent = other.parent

    # Fields getters
    @property
    def place_price(self) -> float | None:
        """Getter of place_price

        Returns:
            float | None: `float` or `None`
        """
        if self.type == OrderType.Limit:
            return self.limit_price
        if self.type == OrderType.Stop:
            return self.stop_price
        return None

    @property
    def limit(self) -> float | None:
        """Getter of limit_price

        Returns:
            float | None: `float` or `None`
        """
        return self.limit_price

    @property
    def stop(self) -> float | None:
        """Getter of stop_price

        Returns:
            float | None: `float` or `None`
        """
        return self.stop_price

    @property
    def sl(self) -> float | None:
        """Getter of sl_price

        Returns:
            float | None: `float` or `None`
        """
        return self.sl_price

    @property
    def tp(self) -> float | None:
        """Getter of tp_price

        Returns:
            float | None: `float` or `None`
        """
        return self.tp_price

    # Extra properties
    @property
    def is_sl_order(self) -> bool:
        """`Order` is stop-loss order of a `Position`

        Returns:
            bool: _description_
        """
        return self.parent and self is self.parent.sl_order

    @property
    def is_tp_order(self) -> bool:
        """`Order` is take-profit order of a `Position`

        Returns:
            bool: _description_
        """
        return self.parent and self is self.parent.tp_order

    @property
    def is_opening(self) -> bool:
        """Flag to check `Order` still alive

        Returns:
            bool: True if `state` in [OrderState.Pending, OrderState.Placed, OrderState.Partial]
        """
        return self.state in [OrderState.Pending, OrderState.Placed, OrderState.Partial]

    @property
    def is_closed(self) -> bool:
        """Flag to check `Order` closed

        Returns:
            bool: True if `state` in [OrderState.Filled, OrderState.Canceled]
        """
        return self.state in [OrderState.Filled, OrderState.Canceled]


class OrderResult:
    """Result of `Order`"""

    def __init__(
        self,
        ok: bool = True,
        order: "Order | None" = None,
        raw: object | None = None,
    ) -> None:
        """_summary_

        Args:
            ok (bool | None, optional): Flag to check `Order` is success or not. Defaults to True.
            order (Order | None, optional): Order own the result. Defaults to None.
            raw (object | None, optional): Raw object of `Order`. Defaults to None.
        """
        self.ok: bool = ok
        self.order: "Order | None" = order
        self.raw: object | None = raw

    def _repr_params(self):
        params = f"ok={self.ok} order={self.order}"
        if self.raw is not None:
            params += f"raw='{self.raw}'"
        return params

    def __repr__(self):
        return f"<{self.__class__.__name__} {self._repr_params()}>"


class OrderResultOk(OrderResult):
    """Result of a success `Order`"""

    def __init__(
        self,
        order: "Order | None" = None,
        raw: object | None = None,
    ) -> None:
        """_summary_

        Args:
            order (Order | None, optional): Order own the result. Defaults to None.
            raw (object | None, optional): Raw object of `Order`. Defaults to None.
        """
        super().__init__(ok=True, order=order, raw=raw)


class OrderResultError(OrderResult):
    """Result of a error `Order`"""

    def __init__(
        self,
        error: str,
        order: "Order | None" = None,
        raw: object | None = None,
    ) -> None:
        """_summary_

        Args:
            error (str): Error message
            order (Order | None, optional): Order own the result. Defaults to None.
            raw (object | None, optional): Raw object of `Order`. Defaults to None.
        """
        super().__init__(ok=False, order=order, raw=raw)
        self.error: str = error

    def _repr_params(self):
        return f"error={self.error} {super()._repr_params()}"
