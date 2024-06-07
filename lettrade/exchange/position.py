from .base import BaseTransaction


class Position(BaseTransaction):
    def __init__(
        self,
        id: str,
        exchange: "Exchange",
        data: "DataFeed",
        size: float,
    ):
        super().__init__(
            id=id,
            exchange=exchange,
            data=data,
            size=size,
        )

    @property
    def pl(self) -> float:
        """Profit (positive) or loss (negative) of the current position in cash units."""

    @property
    def pl_pct(self) -> float:
        """"""

    def close(self, position: float = 1.0):
        """
        Close position of position by closing `position` of each active trade. See `Trade.close`.
        """

    def __repr__(self):
        return f"<Position: {self.size}>"

    def merge(self, other: "Position"):
        """"""
