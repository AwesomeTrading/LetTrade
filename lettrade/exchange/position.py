import numpy as np
import pandas as pd


class Position:
    def __init__(self, exchange: "Exchange"):
        self.__exchange = exchange

    def __bool__(self):
        return self.size != 0

    @property
    def size(self) -> float:
        """Position size in units of asset. Negative if position is short."""
        return sum(trade.size for trade in self.__exchange.trades)

    @property
    def pl(self) -> float:
        """Profit (positive) or loss (negative) of the current position in cash units."""
        return sum(trade.pl for trade in self.__exchange.trades)

    @property
    def pl_pct(self) -> float:
        """Profit (positive) or loss (negative) of the current position in percent."""
        weights = np.abs([trade.size for trade in self.__exchange.trades])
        weights = weights / weights.sum()
        pl_pcts = np.array([trade.pl_pct for trade in self.__exchange.trades])
        return (pl_pcts * weights).sum()

    @property
    def is_long(self) -> bool:
        """True if the position is long (position size is positive)."""
        return self.size > 0

    @property
    def is_short(self) -> bool:
        """True if the position is short (position size is negative)."""
        return self.size < 0

    def close(self, portion: float = 1.0):
        """
        Close portion of position by closing `portion` of each active trade. See `Trade.close`.
        """
        for trade in self.__exchange.trades:
            trade.close(portion)

    def __repr__(self):
        return f"<Position: {self.size} ({len(self.__exchange.trades)} trades)>"

    def merge(self, other: "Position"):
        if other is self:
            return

        # if self.id != other.id:
        #     raise RuntimeError(f"Merge difference id {self.id} != {other.id} order")

        # self.size = other.size
        # if other.sl_order:
        #     self.sl_order = other.sl_order
        # if other.tp_order:
        #     self.tp_order = other.tp_order

        # if other.entry_price:
        #     self.entry_price = other.entry_price
        # if other.entry_at:
        #     self.entry_at = other.entry_at

        # if other.exit_price:
        #     self.exit_price = other.exit_price
        # if other.exit_at:
        #     self.exit_at = other.exit_at
        # if other.parent:
        #     self.parent = other.parent
