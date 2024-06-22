from typing import Optional

from lettrade.account import Account


class BackTestAccount(Account):
    _commission: float

    def __init__(
        self,
        risk: float = 0.02,
        cash: float = 10_000,
        commission: float = 0.2,
        margin: float = 1,
        leverage: float = 1,
        **kwargs,
    ) -> None:
        """Account for backtest

        Args:
            risk (float, optional): _description_. Defaults to 0.02.
            cash (float, optional): _description_. Defaults to 10_000.
            commission (float, optional): Commission fee is percent of size. Defaults to 0.2.
            margin (float, optional): _description_. Defaults to 1.
            leverage (float, optional): _description_. Defaults to 1.
            **kwargs (dict, optional): Mirror of [lettrade.account.Account()](site:/reference/account/account/#lettrade.account.account.Account).
        """
        super().__init__(
            risk=risk,
            cash=cash,
            margin=margin,
            leverage=leverage,
            **kwargs,
        )
        self._commission = commission

    def __repr__(self):
        return "<BackTestAccount " + str(self) + ">"

    def pl(self, size, entry_price: float, exit_price: Optional[float] = None) -> float:
        if exit_price is None:
            exit_price = self._exchange.data.l.open[0]

        pl = size * (exit_price - entry_price)

        return pl

    def fee(self, size: float, **kwargs: dict):
        return -abs(size * self._commission)


class ForexBackTestAccount(BackTestAccount):
    """Forex backtest account helps to handle lot size"""

    def __repr__(self):
        return "<ForexBackTestAccount " + str(self) + ">"

    def pl(self, size, entry_price: float, exit_price: Optional[float] = None) -> float:
        return super().pl(size, entry_price, exit_price) * 100_000
