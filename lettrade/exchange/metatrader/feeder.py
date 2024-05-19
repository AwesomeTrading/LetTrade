import time

from lettrade.data import DataFeeder

from .api import MetaTraderAPI
from .data import MetaTraderDataFeed


class MetaTraderDataFeeder(DataFeeder):
    datas: list[MetaTraderDataFeed]
    data: MetaTraderDataFeed

    _api: MetaTraderAPI
    _tick: bool

    def __init__(self, api: MetaTraderAPI, tick: bool = 5) -> None:
        """
        tick:
            tick < 0: no tick, just get completed bar
            tick == 0: wait until new bar change value
            tick > 0: sleep tick time (in seconds) then update
        """
        super().__init__()
        self._api = api
        self._tick = tick

    def alive(self):
        return self._api.heartbeat()

    def next(self):
        if self._tick > 0:
            time.sleep(self._tick)

        return self.data.next(tick=self._tick)

    def start(self, size=100):
        for data in self.datas:
            data._next(size=size, tick=self._tick)
