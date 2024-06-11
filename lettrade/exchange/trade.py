from typing import Optional

import pandas as pd

from .base import BaseTransaction, TradeState
from .order import Order


class Trade(BaseTransaction):
    """
    When an `Order` is filled, it results in an active `Trade`.
    Find active trades in `Strategy.trades` and closed, settled trades in `Strategy.closed_trades`.
    """

    def __init__(
        self,
        id: str,
        exchange: "Exchange",
        data: "DataFeed",
        size: float,
        parent: "Order",
        tag: object = "",
        state: TradeState = TradeState.Open,
        entry_price: Optional[float] = None,
        entry_fee: float = 0.0,
        entry_at: Optional[pd.Timestamp] = None,
        sl_order: Optional[Order] = None,
        tp_order: Optional[Order] = None,
    ):
        super().__init__(
            id=id,
            exchange=exchange,
            data=data,
            size=size,
        )
        self._account: "Account" = self.exchange._account

        self.state: TradeState = state
        self.tag: object = tag
        self.parent: "Order" = parent

        self.entry_price: Optional[float] = entry_price
        self.entry_fee: float = entry_fee
        self.entry_at: Optional[pd.Timestamp] = entry_at

        self.exit_price: Optional[float] = None
        self.exit_fee: float = 0.0
        self.exit_at: Optional[pd.Timestamp] = None
        self.exit_pl: Optional[float] = None

        self.sl_order: Optional[Order] = sl_order
        self.tp_order: Optional[Order] = tp_order

    def __repr__(self):
        return (
            f"<Trade id={self.id} state={self.state} size={self.size} "
            f"sl={self.sl} tp={self.tp}, pl={self.pl} tag='{self.tag}' >"
        )

    # return (
    #     f'<Trade id={self.id} size={self.size} time={self.entry_at}-{self.exit_at or ""} '
    #     f'price={self.entry_price}-{self.exit_price or ""} pl={self.pl:.0f}'
    #     f'{" tag="+str(self.tag) if self.tag is not None else ""}>'
    # )

    def _on_entry(self, price: float, at: pd.Timestamp, fee: float) -> bool:
        self.entry_price = price
        self.entry_at = at
        self.entry_fee = fee
        self.state = TradeState.Open
        self.exchange.on_trade(self)
        return True

    def _on_exit(self, price: float, at: pd.Timestamp, pl: float, fee: float) -> bool:
        if self.state != TradeState.Open:
            return False

        self.exit_price = price
        self.exit_at = at
        self.exit_pl = pl
        self.exit_fee = fee
        self.state = TradeState.Exit
        self.exchange.on_trade(self)
        return True

    def update(self, sl=None, tp=None, **kwargs):
        """"""
        raise NotImplementedError

    def exit(self):
        """"""
        raise NotImplementedError

    def merge(self, other: "Trade"):
        if other is self:
            return

        if self.id != other.id:
            raise RuntimeError(f"Merge difference id {self.id} != {other.id} order")

        self.size = other.size
        if other.sl_order:
            self.sl_order = other.sl_order
        if other.tp_order:
            self.tp_order = other.tp_order

        if other.entry_price:
            self.entry_price = other.entry_price
        if other.entry_at:
            self.entry_at = other.entry_at

        if other.exit_price:
            self.exit_price = other.exit_price
        if other.exit_at:
            self.exit_at = other.exit_at
        if other.parent:
            self.parent = other.parent

    # Extra properties
    @property
    def sl(self) -> float | None:
        if self.sl_order:
            return self.sl_order.stop_price
        return None

    @property
    def tp(self) -> float | None:
        if self.tp_order:
            return self.tp_order.limit_price
        return None

    @property
    def is_exited(self) -> bool:
        """Flag to check Trade state.

        Returns:
            bool: True if the trade exited
        """
        return self.state == TradeState.Exit

    @property
    def pl(self) -> float:
        """Estimate Profit or Loss of Trade

        Returns:
            float: PnL
        """
        if self.state == TradeState.Exit:
            pl = self.exit_pl
        else:
            pl = self._account.pl(size=self.size, entry_price=self.entry_price)
        return pl + self.fee

    @property
    def fee(self) -> float:
        """Fee/Estimate Fee for trade

        Returns:
            float: Fee
        """
        return self.entry_fee + self.exit_fee
