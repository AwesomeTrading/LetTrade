from typing import Type

from .. import Execute, Order, OrderState, OrderType, Trade, TradeState


class BackTestExecute(Execute):
    """
    Execute for BackTest
    """


class BackTestOrder(Order):
    _trade_cls: Type["Trade"] = None
    _execute_cls: Type["Execute"] = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def place(self):
        if self.state != OrderState.Pending:
            raise RuntimeError(f"Order {self.id} state {self.state} is not Pending")
        self.state = OrderState.Place
        self.exchange.on_order(self)

    def cancel(self):
        """Cancel the order."""
        if self.state is not OrderState.Place:
            return

        self.state = OrderState.Canceled
        if self.trade:
            if self is self.trade.sl_order:
                self.trade.sl_order = None
            elif self is self.trade.tp_order:
                self.trade.tp_order = None

        self.exchange.on_order(self)

    def execute(self, price, bar):
        if self.state != OrderState.Place:
            raise RuntimeError(f"Execute a {self.state} order")

        # Order
        super().execute(price=price, bar=bar)

        # Execute
        execute: BackTestExecute = self.build_execute(
            id=self.exchange._id(),
            price=price,
            bar=bar,
        )
        execute.execute()

        # Trade hit SL/TP
        if self.trade:
            self.trade.exit(price=price, bar=bar, caller=self)
        else:
            # Trade: Place and create new trade
            trade = self.build_trade(id=self.exchange._id())
            if self.sl_price:
                trade._new_sl_order()
            if self.tp_price:
                trade._new_tp_order()
            trade.entry(price=price, bar=bar)

        return execute

    def build_execute(
        self,
        id,
        price,
        bar,
        size=None,
        exchange=None,
        data=None,
    ) -> "Execute":
        return BackTestOrder._execute_cls(
            id=id,
            size=size or self.size,
            exchange=exchange or self.exchange,
            data=data or self.data,
            price=price,
            bar=bar,
            parent=self,
        )

    def build_trade(
        self,
        id,
        exchange=None,
        data=None,
        size=None,
        state=TradeState.Open,
    ) -> "BackTestTrade":
        trade = BackTestOrder._trade_cls(
            id=id,
            size=size or self.size,
            exchange=exchange or self.exchange,
            data=data or self.data,
            state=state,
            parent=self,
        )
        self.trade = trade
        return trade


class BackTestTrade(Trade):
    _order_cls: Type["BackTestOrder"] = None

    def exit(self, price, bar, caller=None):
        if self.state != TradeState.Open:
            return

        # State
        super().exit(price=price, bar=bar, pl=self.pl, fee=0)

        # Caller is trade close by tp/sl order
        if caller is None or (self.sl_order and self.sl_order is not caller):
            self.sl_order.cancel()
        if caller is None or (self.tp_order and self.tp_order is not caller):
            self.tp_order.cancel()

    def _new_sl_order(self) -> BackTestOrder:
        if self.sl_order:
            raise RuntimeError(f"Trade {self.id} SL Order {self.sl_order} existed")

        sl_order = BackTestOrder(
            id=self.exchange._id(),
            exchange=self.exchange,
            data=self.parent.data,
            size=-self.size,
            type=OrderType.Stop,
            stop_price=self.parent.sl_price,
            tag=self.parent.tag,
            open_bar=self.data.bar(),
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
            id=self.exchange._id(),
            exchange=self.exchange,
            data=self.parent.data,
            size=-self.size,
            type=OrderType.Limit,
            limit_price=self.parent.tp_price,
            tag=self.parent.tag,
            open_bar=self.data.bar(),
            open_price=self.parent.tp_price,
            trade=self,
        )
        self.tp_order = tp_order
        tp_order.place()
        return tp_order
