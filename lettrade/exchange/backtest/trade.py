from typing import Optional

from .. import Execution, Order, OrderState, OrderType, Position, PositionState


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

    def update(self, limit_price=None, stop_price=None, sl=None, tp=None, **kwargs):
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

    def cancel(self):
        self._on_cancel()

    def _on_cancel(self):
        """Cancel the Order and notify Exchange"""
        if self.state is not OrderState.Placed:
            return

        self.state = OrderState.Canceled
        if self.parent:
            if self is self.parent.sl_order:
                self.parent.sl_order = None
            elif self is self.parent.tp_order:
                self.parent.tp_order = None

        self.exchange.on_order(self)

    def _on_fill(self, price: float, at: object) -> BackTestExecution:
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
        ok = super()._on_fill(price=price, at=at)

        # Execution is enable
        if self.exchange.executions is not None:
            execution = BackTestExecution.from_order(order=self, price=price, at=at)
            execution._on_execution()

        # Position hit SL/TP
        if self.parent:
            self.parent._on_exit(price=price, at=at, caller=self)
        else:
            # Position: Place and create new position
            position = BackTestPosition.from_order(order=self)

            position._on_entry(price=price, at=at)

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

    def update(self, sl=None, tp=None, **kwargs):
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

        # Refresh position
        self.exchange.on_position(self)

    def exit(self):
        self._on_exit(
            price=self.data.l.open[0],
            at=self.data.bar(),
        )

    def _on_entry(self, price: float, at: object) -> bool:
        # Fee
        fee = self._account.fee(size=self.size)
        return super()._on_entry(price, at, fee)

    def _on_exit(
        self,
        price: float,
        at: object,
        caller: Optional[Order | Position] = None,
    ):
        """Exit Position

        Args:
            price (float): Exit price
            at (object): Exit bar
            caller (Order | Position, optional): Skip caller to prevent infinite recursion loop. Defaults to None.
        """
        if self.state != PositionState.Open:
            return

        # PnL
        pl = self._account.pl(
            size=self.size,
            entry_price=self.entry_price,
            exit_price=price,
        )

        # Fee
        fee = self._account.fee(size=self.size)

        # State
        super()._on_exit(price=price, at=at, pl=pl, fee=fee)

        # Caller is position close by tp/sl order
        if caller is None or (self.sl_order and self.sl_order is not caller):
            self.sl_order._on_cancel()
        if caller is None or (self.tp_order and self.tp_order is not caller):
            self.tp_order._on_cancel()

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
        sl_order._on_place(at=self.data.bar())
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
        tp_order._on_place(at=self.data.bar())
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
