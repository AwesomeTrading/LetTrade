import time

from lettrade.data import DataFeeder

from .api import LiveAPI
from .data import LiveDataFeed


class LiveDataFeeder(DataFeeder):
    datas: list[LiveDataFeed]
    data: LiveDataFeed

    _api: LiveAPI
    _tick: bool

    def __init__(self, api: LiveAPI, tick: bool = 5) -> None:
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
        for data in self.datas:
            data.next(tick=self._tick)

    def start(self, size=100):
        for data in self.datas:
            data._next(size=size, tick=self._tick)
