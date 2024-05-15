import logging

from lettrade.account import Account

from .api import MetaTraderAPI

logger = logging.getLogger(__name__)


class MetaTraderAccount(Account):
    _api: MetaTraderAPI
    _account: object

    def __init__(self, api: MetaTraderAPI, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._api = api

    def __repr__(self):
        return "<MetaTraderAccount " + str(self) + ">"

    def start(self):
        self._account = self._api.account()
        logger.info("Account: %s", str(self._account))
