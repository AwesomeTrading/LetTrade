import time
from typing import Type

from lettrade.data import DataFeeder

from .api import LiveAPI
from .data import LiveDataFeed


class LiveDataFeeder(DataFeeder):
    # Class properties
    _api_cls: Type[LiveAPI] = LiveAPI
    _data_cls: Type[LiveDataFeed] = LiveDataFeed

    # Object properties
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

    def start(self, size=100):
        for data in self.datas:
            data.next(size=size, tick=self._tick)

    def next(self):
        if self._tick > 0:
            time.sleep(self._tick)
        for data in self.datas:
            data.next(tick=self._tick)

    ### Extend
    def data_new(self, **kwargs):
        return self._data_cls(api=self._api, **kwargs)

    def markets(self, search=None):
        return self._api.markets(search=search)

    @classmethod
    def instance(
        cls,
        api: LiveAPI = None,
        api_kwargs: dict = None,
        **kwargs,
    ) -> "LiveDataFeed":
        """_summary_

        Args:
            api (LiveAPI, optional): _description_. Defaults to None.
            api_kwargs (dict, optional): _description_. Defaults to None.

        Raises:
            RuntimeError: Missing api requirement

        Returns:
            LiveDataFeed: DataFeed object
        """
        if api is None:
            if api_kwargs is None:
                raise RuntimeError("api or api_kwargs cannot missing")
            api = cls._api_cls(**api_kwargs)
        obj = cls(api=api, **kwargs)
        return obj
