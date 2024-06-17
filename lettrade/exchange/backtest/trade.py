from typing import Optional

from .. import Execute, Order, OrderState, OrderType, Position, PositionState


class BackTestExecute(Execute):
    """
    Execute for backtesting
    """


class BackTestOrder(Order):
    """Order for backtesting"""

    position: "BackTestPosition"

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
        if self.position:
            if self is self.position.sl_order:
                self.position.sl_order = None
            elif self is self.position.tp_order:
                self.position.tp_order = None

        self.exchange.on_order(self)

    def _on_execute(self, price: float, at: object) -> BackTestExecute:
        """Execute order and notify for Exchange

        Args:
            price (float): Executed price
            at (object): Executed bar

        Raises:
            RuntimeError: _description_

        Returns:
            BackTestExecute: Execute object
        """
        if self.state != OrderState.Placed:
            raise RuntimeError(f"Execute a {self.state} order")

        # Order
        super()._on_execute(price=price, at=at)

        # Execute
        execute = self._build_execute(price=price, at=at)
        execute._on_execute()

        # Trade hit SL/TP
        if self.position:
            self.position._on_exit(price=price, at=at, caller=self)
        else:
            # Trade: Place and create new trade
            trade = self._build_position()

            trade._on_entry(price=price, at=at)

        return execute

    def _build_execute(
        self,
        price: float,
        at: object,
        size: Optional[float] = None,
    ) -> BackTestExecute:
        """Method help to build Execute object from Order object

        Args:
            price (float): Executed price
            at (object): Executed bar
            size (Optional[float], optional): Executed size. Defaults to None.

        Returns:
            BackTestExecute: Execute object
        """
        return BackTestExecute(
            id=self.id,
            size=size or self.size,
            exchange=self.exchange,
            data=self.data,
            price=price,
            at=at,
            order=self,
        )

    def _build_position(
        self,
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
        position = BackTestPosition(
            id=self.id,
            size=size or self.size,
            exchange=self.exchange,
            data=self.data,
            state=state,
            parent=self,
        )
        if self.sl_price:
            position._new_sl_order(stop_price=self.sl_price)
        if self.tp_price:
            position._new_tp_order(limit_price=self.tp_price)
        self.position = position
        return position


class BackTestPosition(Position):
    """Position for backtesting"""

    def update(self, sl=None, tp=None, **kwargs):
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

        # Refresh trade
        self.exchange.on_trade(self)

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

        # Caller is trade close by tp/sl order
        if caller is None or (self.sl_order and self.sl_order is not caller):
            self.sl_order._on_cancel()
        if caller is None or (self.tp_order and self.tp_order is not caller):
            self.tp_order._on_cancel()

    def _new_sl_order(self, stop_price: float) -> BackTestOrder:
        # Validate
        if self.sl_order:
            raise RuntimeError(f"Position {self.id} SL Order {self.sl_order} existed")

        sl_order = BackTestOrder(
            id=f"{self.id}-sl",
            exchange=self.exchange,
            data=self.data,
            size=-self.size,
            type=OrderType.Stop,
            stop_price=stop_price,
            tag=self.tag,
            open_at=self.data.bar(),
            open_price=stop_price,
            position=self,
        )
        self.sl_order = sl_order
        sl_order._on_place()
        return sl_order

    def _new_tp_order(self, limit_price: float) -> BackTestOrder:
        # TODO: validate price
        if self.tp_order:
            raise RuntimeError(f"Position {self.id} TP Order {self.tp_order} existed")

        tp_order = BackTestOrder(
            id=f"{self.id}-tp",
            exchange=self.exchange,
            data=self.data,
            size=-self.size,
            type=OrderType.Limit,
            limit_price=limit_price,
            tag=self.tag,
            open_at=self.data.bar(),
            open_price=limit_price,
            position=self,
        )
        self.tp_order = tp_order
        tp_order._on_place()
        return tp_order
