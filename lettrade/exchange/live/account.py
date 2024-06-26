import logging

from lettrade.account import Account

from .api import LiveAPI
from .trade import LivePosition

logger = logging.getLogger(__name__)


class LiveAccount(Account):
    _api: LiveAPI
    _account: object

    _balance: float
    _equity: float

    def __init__(self, api: LiveAPI, **kwargs) -> None:
        """Account for live trading

        Args:
            api (LiveAPI): _description_
            **kwargs (dict, optional): Mirror of [lettrade.account.Account()](site:/reference/account/account/#lettrade.account.account.Account).
        """
        super().__init__(**kwargs)
        self._api = api

        self._balance = 0.0
        self._equity = 0.0

    # def __repr__(self):
    #     return "<LiveAccount " + str(self) + ">"

    def start(self):
        """Start live account by load account info from API"""
        self.account_refresh()
        self._margin = self._account.margin
        self._leverage = self._account.leverage

    # def next(self):
    #     """Live account next"""
    #     self.account_refresh()
    #     return super().next()

    def pl(self, size, entry_price: float, exit_price: float | None = None) -> float:
        if exit_price is None:
            exit_price = self._exchange.data.l.open[0]

        pl = size * (exit_price - entry_price)

        return pl * 100_000

    def account_refresh(self):
        """Refresh account balance"""
        self._account = self._api.account()

        if __debug__:
            logger.debug("Account: %s", str(self._account))

        self._balance = self._account.balance
        self._equity = self._account.equity

    def on_positions(self, positions: list[LivePosition]):
        self.account_refresh()
        return super().on_positions(positions)

    @property
    def equity(self) -> float:
        return self._equity
