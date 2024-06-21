from typing import Optional

import pandas as pd

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


class BackTestExecution(Execution):
    """
    Execution for backtesting
    """

    @classmethod
    def from_order(
        cls,
        order: "BackTestOrder",
        price: float,
        at: object,
        size: Optional[float] = None,
    ) -> "BackTestExecution":
        """Method help to build Execution object from Order object

        Args:
            price (float): Executed price
            at (object): Executed bar
            size (Optional[float], optional): Executed size. Defaults to None.

        Returns:
            BackTestExecution: Execution object
        """
        return cls(
            id=order.id,
            size=size or order.size,
            exchange=order.exchange,
            data=order.data,
            price=price,
            at=at,
            order=order,
        )


class BackTestOrder(Order):
    """Order for backtesting"""

    parent: "BackTestPosition"

    def cancel(self) -> "OrderResult":
        """Cancel the Order and notify Exchange"""
        if self.state != OrderState.Placed:
            raise RuntimeError(f"Order {self.id} state {self.state} is not Placed")

        if self.parent:
            if self is self.parent.sl_order:
                self.parent.sl_order = None
            elif self is self.parent.tp_order:
                self.parent.tp_order = None

        return super().cancel()

    def fill(self, price: float, at: object) -> BackTestExecution:
        """Execution order and notify for Exchange

        Args:
            price (float): Executed price
            at (object): Executed bar

        Raises:
            RuntimeError: _description_

        Returns:
            BackTestExecution: Execution object
        """
        if self.state != OrderState.Placed:
            raise RuntimeError(f"Execution a {self.state} order")

        # Order
        ok = super().fill(price=price, at=at)

        # Execution is enable
        if self.exchange.executions is not None:
            execution = BackTestExecution.from_order(order=self, price=price, at=at)
            execution._on_execution()

        # Position hit SL/TP
        if self.parent:
            self.parent.exit(price=price, at=at, caller=self)
        else:
            # Position: Place and create new position
            position = BackTestPosition.from_order(order=self)

            position.entry(price=price, at=at)

        return ok

    @classmethod
    def from_position(
        cls,
        position: "BackTestPosition",
        id: str,
        type: OrderType,
        limit_price: float = None,
        stop_price: float = None,
    ) -> "BackTestOrder":
        order = cls(
            id=id,
            exchange=position.exchange,
            data=position.data,
            size=-position.size,
            type=type,
            limit_price=limit_price,
            stop_price=stop_price,
            tag=position.tag,
            parent=position,
        )
        return order


class BackTestPosition(Position):
    """Position for backtesting"""

    def update(self, sl=None, tp=None, **kwargs) -> PositionResult:
        if not sl and not tp:
            raise RuntimeError("Update sl=None and tp=None")

        if sl is not None:
            if self.sl_order:
                self.sl_order.update(stop_price=sl)
            else:
                self._new_sl_order(stop_price=sl)

        if tp is not None:
            if self.tp_order:
                self.tp_order.update(limit_price=tp)
            else:
                self._new_tp_order(limit_price=tp)

        super().update()

    def entry(self, price: float, at: object) -> PositionResult:
        # Fee
        fee = self._account.fee(size=self.size)
        return super().entry(price, at, fee)

    def exit(
        self,
        price: Optional[float] = None,
        at: Optional[pd.Timestamp] = None,
        caller: Optional[Order | Position] = None,
    ) -> PositionResult:
        """Exit Position

        Args:
            price (float): Exit price
            at (object): Exit bar
            caller (Order | Position, optional): Skip caller to prevent infinite recursion loop. Defaults to None.
        """
        if self.state != PositionState.Open:
            if caller is None:
                # Call by user
                raise RuntimeError(f"Call exited position {self}")
            return

        if caller is None:
            # Call by user
            if price is not None:
                raise RuntimeError(f"Price set {price} is not available")
            if at is not None:
                raise RuntimeError(f"At set {at} is not available")

            price = self.data.l.open[0]
            at = self.data.l.index[0]
        else:
            # Call by SL/TP order
            if price is None or at is None:
                raise RuntimeError(f"Caller {caller} with price is None or at is None")

        # PnL
        pl = self._account.pl(
            size=self.size,
            entry_price=self.entry_price,
            exit_price=price,
        )

        # Fee
        fee = self._account.fee(size=self.size)

        # State
        ok = super().exit(price=price, at=at, pl=pl, fee=fee)

        # Caller is position close by tp/sl order
        if caller is None:
            if self.sl_order is not None:
                self.sl_order.cancel(caller=self)
            if self.tp_order is not None:
                self.tp_order.cancel(caller=self)
        else:
            if self.sl_order and self.sl_order is not caller:
                self.sl_order.cancel(caller=caller)
            if self.tp_order and self.tp_order is not caller:
                self.tp_order.cancel(caller=caller)

        return ok

    def _new_sl_order(self, stop_price: float) -> BackTestOrder:
        if self.sl_order:
            raise RuntimeError(f"Position {self.id} SL Order {self.sl_order} existed")

        sl_order = BackTestOrder.from_position(
            position=self,
            id=f"{self.id}-sl",
            type=OrderType.Stop,
            stop_price=stop_price,
        )
        self.sl_order = sl_order
        sl_order.place(at=self.data.bar())
        return sl_order

    def _new_tp_order(self, limit_price: float) -> BackTestOrder:
        if self.tp_order:
            raise RuntimeError(f"Position {self.id} TP Order {self.tp_order} existed")

        tp_order = BackTestOrder.from_position(
            position=self,
            id=f"{self.id}-tp",
            type=OrderType.Limit,
            limit_price=limit_price,
        )

        self.tp_order = tp_order
        tp_order.place(at=self.data.bar())
        return tp_order

    @classmethod
    def from_order(
        cls,
        order: "BackTestOrder",
        size: Optional[float] = None,
        state: PositionState = PositionState.Open,
    ) -> "BackTestPosition":
        """Build Position object from Order object

        Args:
            size (float, optional): Size of Position object. Defaults to None.
            state (PositionState, optional): State of Position object. Defaults to PositionState.Open.

        Returns:
            BackTestPosition: Position object
        """
        position = cls(
            id=order.id,
            size=size or order.size,
            exchange=order.exchange,
            data=order.data,
            state=state,
            parent=order,
        )
        if order.sl_price:
            position._new_sl_order(stop_price=order.sl_price)
        if order.tp_price:
            position._new_tp_order(limit_price=order.tp_price)
        order.parent = position
        return position
