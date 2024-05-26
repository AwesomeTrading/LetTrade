import logging

from lettrade.account import Account

from .api import LiveAPI

logger = logging.getLogger(__name__)


class LiveAccount(Account):
    _api: LiveAPI
    _account: object

    def __init__(self, api: LiveAPI, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._api = api

    # def __repr__(self):
    #     return "<LiveAccount " + str(self) + ">"

    def start(self):
        self._account = self._api.account()
        logger.info("Account: %s", str(self._account))
