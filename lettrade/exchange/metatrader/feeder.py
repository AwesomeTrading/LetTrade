import time

from lettrade.data import DataFeeder

from .api import MetaTraderAPI
from .data import MetaTraderDataFeed


class MetaTraderDataFeeder(DataFeeder):
    datas: list[MetaTraderDataFeed]
    data: MetaTraderDataFeed

    _api: MetaTraderAPI

    def __init__(self, api: MetaTraderAPI) -> None:
        super().__init__()
        self._api = api

    def alive(self):
        return self._api.heartbeat()

    def next(self):
        time.sleep(5)
        return self.data.next()

    def pre_feed(self, size=100):
        print("pre_feed", size)
        for data in self.datas:
            data._next(size)
