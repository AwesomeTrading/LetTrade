from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING, Optional

import pandas as pd

from .base import BaseTransaction, PositionState
from .order import Order

if TYPE_CHECKING:
    from lettrade.account import Account
    from lettrade.data import DataFeed
    from lettrade.exchange import Exchange


class Position(BaseTransaction, metaclass=ABCMeta):
    """
    When an `Order` is filled, it results in an active `Position`.
    Find active positions in `Strategy.positions` and closed, settled positions in `Strategy.closed_positions`.
    """

    def __init__(
        self,
        id: str,
        exchange: "Exchange",
        data: "DataFeed",
        size: float,
        parent: "Order",
        tag: object = "",
        state: PositionState = PositionState.Open,
        entry_price: Optional[float] = None,
        entry_fee: float = 0.0,
        entry_at: Optional[pd.Timestamp] = None,
        sl_order: Optional[Order] = None,
        tp_order: Optional[Order] = None,
        **kwargs,
    ):
        super().__init__(
            id=id,
            exchange=exchange,
            data=data,
            size=size,
            **kwargs,
        )
        self._account: "Account" = self.exchange._account

        self.state: PositionState = state
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
            f"<{self.__class__.__name__} id={self.id} state={self.state} size={self.size} "
            f"sl={self.sl} tp={self.tp}, pl={round(self.pl, 5)} tag='{self.tag}' >"
        )

    def entry(
        self,
        price: float,
        at: pd.Timestamp,
        fee: float,
        raw: Optional[object] = None,
    ) -> "PositionResult":
        self.entry_price = price
        self.entry_at = at
        self.entry_fee = fee
        self.state = PositionState.Open
        self.exchange.on_position(self)
        return PositionResultOk(position=self, raw=raw)

    def update(self, raw: Optional[object] = None, **kwargs) -> "PositionResult":
        self.exchange.on_position(self)
        return PositionResultOk(position=self, raw=raw)

    def exit(
        self,
        price: float,
        at: pd.Timestamp,
        pl: float,
        fee: float,
        raw: Optional[object] = None,
    ) -> "PositionResult":
        if self.state != PositionState.Open:
            return PositionResultError(
                f"Position state {self.state} != PositionState.Open",
                code=-1,
                position=self,
                raw=raw,
            )

        self.exit_price = price
        self.exit_at = at
        self.exit_pl = pl
        self.exit_fee = fee
        self.state = PositionState.Exit
        self.exchange.on_position(self)
        return PositionResultOk(position=self, raw=raw)

    def merge(self, other: "Position") -> bool:
        """Merge position from another position has same id

        Args:
            other (Position): _description_

        Raises:
            RuntimeError: _description_
        """
        if other is self:
            return False

        if self.id != other.id:
            raise RuntimeError(f"Merge difference id {self.id} != {other.id} order")

        self.size = other.size

        if other.sl_order is not None:
            self.sl_order = other.sl_order
            self.sl_order.parent = self
        elif self.sl_order is not None:
            self.sl_order.cancel()
            self.sl_order = None

        if other.tp_order is not None:
            self.tp_order = other.tp_order
            self.tp_order.parent = self
        elif self.tp_order is not None:
            self.tp_order.cancel()
            self.tp_order = None

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

        return True

    # Extra properties
    @property
    def sl(self) -> Optional[float]:
        if self.sl_order:
            return self.sl_order.stop_price
        return None

    @property
    def tp(self) -> Optional[float]:
        if self.tp_order:
            return self.tp_order.limit_price
        return None

    @property
    def is_opening(self) -> bool:
        """Flag to check Position state.

        Returns:
            bool: True if the trade opening
        """
        return self.state == PositionState.Open

    @property
    def is_exited(self) -> bool:
        """Flag to check Position state.

        Returns:
            bool: True if the trade exited
        """
        return self.state == PositionState.Exit

    @property
    def pl(self) -> float:
        """Estimate Profit or Loss of Position

        Returns:
            float: PnL
        """
        if self.state == PositionState.Exit:
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


class PositionResult:
    """Result of `Position`"""

    def __init__(
        self,
        ok: bool = True,
        code: int = 0,
        position: Optional["Position"] = None,
        raw: Optional[object] = None,
    ) -> None:
        """_summary_

        Args:
            ok (Optional[bool], optional): Flag to check `Position` is success or not. Defaults to True.
            position (Optional[Position], optional): Position own the result. Defaults to None.
            code (Optional[int], optional): Error code of result. Defaults to 0.
            raw (Optional[object], optional): Raw object of `Position`. Defaults to None.
        """
        self.ok: bool = ok
        self.code: int = code
        self.position: Optional["Position"] = position
        self.raw: Optional[object] = raw


class PositionResultOk(PositionResult):
    """Result of a success `Position`"""

    def __init__(
        self,
        position: Optional["Position"] = None,
        raw: Optional[object] = None,
    ) -> None:
        """_summary_

        Args:
            position (Optional[Position], optional): Position own the result. Defaults to None.
            raw (Optional[object], optional): Raw object of `Position`. Defaults to None.
        """
        super().__init__(ok=True, position=position, raw=raw)


class PositionResultError(PositionResult):
    """Result of a error `Position`"""

    def __init__(
        self,
        error: str,
        code: int,
        position: Optional["Position"] = None,
        raw: Optional[object] = None,
    ) -> None:
        """_summary_

        Args:
            error (str): Error message
            code (int): Error code of result
            position (Optional[Position], optional): Position own the result. Defaults to None.
            raw (Optional[object], optional): Raw object of `Position`. Defaults to None.
        """
        super().__init__(ok=False, position=position, code=code, raw=raw)
        self.error: str = error
