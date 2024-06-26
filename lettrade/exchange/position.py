from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING

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
        state: PositionState = PositionState.Open,
        entry_price: float | None = None,
        entry_fee: float = 0.0,
        entry_at: pd.Timestamp | None = None,
        sl_order: Order | None = None,
        tp_order: Order | None = None,
        tag: str | None = None,
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
        self.parent: "Order" = parent
        self.tag: str | None = tag

        self.entry_price: float | None = entry_price
        self.entry_fee: float = entry_fee
        self.entry_at: pd.Timestamp | None = entry_at

        self.exit_price: float | None = None
        self.exit_fee: float = 0.0
        self.exit_at: pd.Timestamp | None = None
        self.exit_pl: float | None = None

        self.sl_order: Order | None = sl_order
        self.tp_order: Order | None = tp_order

    def _repr_params(self):
        params = (
            f"id='{self.id}'"
            f", state='{self.state}'"
            f", size={round(self.size, 5)}"
            f", entry_price={self.entry_price}"
            f", exit_fee={self.exit_fee}"
            f", entry_at={self.entry_at}"
        )

        if self.sl_order:
            params += f", sl_order={self.sl_order}"
        if self.tp_order:
            params += f", tp_order={self.tp_order}"

        if self.is_exited:
            params += (
                f", exit_price={self.exit_price}"
                f", exit_fee={self.exit_fee}"
                f", exit_at={self.exit_at}"
                f", exit_pl={round(self.exit_pl,5)}"
            )

        if self.tag:
            params += f", tag='{self.tag}'"

        return params

    def __repr__(self):
        return f"<{self.__class__.__name__} {self._repr_params()}>"

    def entry(
        self,
        price: float,
        at: pd.Timestamp,
        fee: float,
        raw: object | None = None,
    ) -> "PositionResult":
        self.entry_price = price
        self.entry_at = at
        self.entry_fee = fee
        self.state = PositionState.Open
        self.exchange.on_position(self)
        return PositionResultOk(position=self, raw=raw)

    def update(self, raw: object | None = None, **kwargs) -> "PositionResult":
        self.exchange.on_position(self)
        return PositionResultOk(position=self, raw=raw)

    def exit(
        self,
        price: float,
        at: pd.Timestamp,
        pl: float,
        fee: float,
        raw: object | None = None,
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

        if other.entry_at:
            self.entry_at = other.entry_at
        if other.entry_price:
            self.entry_price = other.entry_price

        if other.exit_at:
            self.exit_at = other.exit_at
        if other.exit_price:
            self.exit_price = other.exit_price
        if other.exit_fee:
            self.exit_fee = other.exit_fee
        if other.exit_pl:
            self.exit_pl = other.exit_pl

        if other.parent:
            self.parent = other.parent

        return True

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
        position: "Position | None" = None,
        raw: object | None = None,
    ) -> None:
        """_summary_

        Args:
            ok (bool | None, optional): Flag to check `Position` is success or not. Defaults to True.
            position (Position | None, optional): Position own the result. Defaults to None.
            raw (object | None, optional): Raw object of `Position`. Defaults to None.
        """
        self.ok: bool = ok
        self.position: "Position | None" = position
        self.raw: object | None = raw

    def _repr_params(self):
        params = f"ok={self.ok} position={self.position}"
        if self.raw is not None:
            params += f"raw='{self.raw}'"
        return params

    def __repr__(self):
        return f"<{self.__class__.__name__} {self._repr_params()}>"


class PositionResultOk(PositionResult):
    """Result of a success `Position`"""

    def __init__(
        self,
        position: "Position | None" = None,
        raw: object | None = None,
    ) -> None:
        """_summary_

        Args:
            position (Position | None, optional): Position own the result. Defaults to None.
            raw (object | None, optional): Raw object of `Position`. Defaults to None.
        """
        super().__init__(ok=True, position=position, raw=raw)


class PositionResultError(PositionResult):
    """Result of a error `Position`"""

    def __init__(
        self,
        error: str,
        position: "Position | None" = None,
        raw: object | None = None,
    ) -> None:
        """_summary_

        Args:
            error (str): Error message
            position (Position | None, optional): Position own the result. Defaults to None.
            raw (object | None, optional): Raw object of `Position`. Defaults to None.
        """
        super().__init__(ok=False, position=position, raw=raw)
        self.error: str = error

    def _repr_params(self):
        return f"error={self.error} {super()._repr_params()}"
