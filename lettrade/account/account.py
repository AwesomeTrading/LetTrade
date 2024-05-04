from abc import ABCMeta


class Account(metaclass=ABCMeta):
    def __init__(
        self,
        *,
        risk=0.02,
        cash=10_000,
        commission=0.0,
        margin=None,
        leverage=1.0,
    ) -> None:
        self._risk: risk
        self._cash: float = cash
        self._commission: float = commission
        self._margin = margin
        self._leverage: float = leverage

    def __repr__(self):
        return "<Account " + str(self) + ">"

    def risk(self, size=None):
        return self._risk
