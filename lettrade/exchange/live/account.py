import logging
from typing import Optional

from lettrade.account import Account
from lettrade.exchange.backtest import BackTestPosition

from .api import LiveAPI

logger = logging.getLogger(__name__)


class LiveAccount(Account):
    _api: LiveAPI
    _account: object

    def __init__(self, api: LiveAPI, **kwargs) -> None:
        """Account for live trading

        Args:
            api (LiveAPI): _description_
            **kwargs (dict, optional): Mirror of [lettrade.account.Account()](site:/reference/account/account/#lettrade.account.account.Account).
        """
        super().__init__(**kwargs)
        self._api = api

    # def __repr__(self):
    #     return "<LiveAccount " + str(self) + ">"

    def start(self):
        """Start live account by load account info from API"""
        self.account_refresh()

    def next(self):
        """Live account next"""
        self.account_refresh()
        return super().next()

    def pl(self, size, entry_price: float, exit_price: Optional[float] = None) -> float:
        if exit_price is None:
            exit_price = self._exchange.data.l.open[0]

        pl = size * (exit_price - entry_price)

        return pl * 100_000

    def account_refresh(self):
        """Refresh account balance"""
        self._account = self._api.account()
        logger.info("Account: %s", str(self._account))

    # def on_positions(self, positions: list[BackTestPosition]):
    #     # self.account_refresh()
    #     return super().on_positions(positions)
