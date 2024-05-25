from typing import Optional

from .. import Execute, Order, OrderState, OrderType, Trade, TradeState


class BackTestExecute(Execute):
    """
    Execute for backtesting
    """


class BackTestOrder(Order):
    """Order for backtesting"""

    trade: "BackTestTrade"

    def cancel(self):
        """Cancel the Order and notify Exchange"""
        if self.state is not OrderState.Placed:
            return

        self.state = OrderState.Canceled
        if self.trade:
            if self is self.trade.sl_order:
                self.trade.sl_order = None
            elif self is self.trade.tp_order:
                self.trade.tp_order = None

        self.exchange.on_order(self)

    def execute(self, price: float, at: object) -> BackTestExecute:
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
        super().execute(price=price, at=at)

        # Execute
        execute: BackTestExecute = self.build_execute(price=price, at=at)
        execute.execute()

        # Trade hit SL/TP
        if self.trade:
            self.trade.exit(price=price, at=at, caller=self)
        else:
            # Trade: Place and create new trade
            trade = self.build_trade()
            if self.sl_price:
                trade._new_sl_order()
            if self.tp_price:
                trade._new_tp_order()
            trade.entry(price=price, at=at)

        return execute

    def build_execute(
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

    def build_trade(
        self,
        size: float = None,
        state: TradeState = TradeState.Open,
    ) -> "BackTestTrade":
        """Build Trade object from Order object

        Args:
            size (float, optional): Size of Trade object. Defaults to None.
            state (TradeState, optional): State of Trade object. Defaults to TradeState.Open.

        Returns:
            BackTestTrade: Trade object
        """
        trade = BackTestTrade(
            id=self.id,
            size=size or self.size,
            exchange=self.exchange,
            data=self.data,
            state=state,
            parent=self,
        )
        self.trade = trade
        return trade


class BackTestTrade(Trade):
    """Trade for backtesting"""

    def entry(self, price: float, at: object) -> bool:
        # Fee
        fee = self._account.fee(size=self.size)
        return super().entry(price, at, fee)

    def exit(self, price: float, at: object, caller: Order | Trade = None):
        """Exit trade

        Args:
            price (float): Exit price
            at (object): Exit bar
            caller (Order | Trade, optional): Skip caller to prevent infinite recursion loop. Defaults to None.
        """
        if self.state != TradeState.Open:
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
        super().exit(price=price, at=at, pl=pl, fee=fee)

        # Caller is trade close by tp/sl order
        if caller is None or (self.sl_order and self.sl_order is not caller):
            self.sl_order.cancel()
        if caller is None or (self.tp_order and self.tp_order is not caller):
            self.tp_order.cancel()

    def _new_sl_order(self) -> BackTestOrder:
        if self.sl_order:
            raise RuntimeError(f"Trade {self.id} SL Order {self.sl_order} existed")

        sl_order = BackTestOrder(
            id=f"{self.id}-sl",
            exchange=self.exchange,
            data=self.parent.data,
            size=-self.size,
            type=OrderType.Stop,
            stop_price=self.parent.sl_price,
            tag=self.parent.tag,
            open_at=self.data.bar(),
            open_price=self.parent.sl_price,
            trade=self,
        )
        self.sl_order = sl_order
        sl_order.place()
        return sl_order

    def _new_tp_order(self) -> BackTestOrder:
        if self.tp_order:
            raise RuntimeError(f"Trade {self.id} TP Order {self.tp_order} existed")

        tp_order = BackTestOrder(
            id=f"{self.id}-tp",
            exchange=self.exchange,
            data=self.parent.data,
            size=-self.size,
            type=OrderType.Limit,
            limit_price=self.parent.tp_price,
            tag=self.parent.tag,
            open_at=self.data.bar(),
            open_price=self.parent.tp_price,
            trade=self,
        )
        self.tp_order = tp_order
        tp_order.place()
        return tp_order
