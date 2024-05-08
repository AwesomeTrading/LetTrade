from lettrade.account import Account

from .api import MetaTraderAPI


class MetaTraderAccount(Account):
    _api: MetaTraderAPI

    def __init__(self, api: MetaTraderAPI, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._api = api

    def __repr__(self):
        return "<MetaTraderAccount " + str(self) + ">"
