import time
from datetime import datetime
from typing import Optional, Type

from lettrade.data import DataFeeder, TimeFrame

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
    _wait_timeframe: TimeFrame

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

        if isinstance(self._tick, int):
            self._wait_timeframe = TimeFrame(f"{self._tick}s")
        else:
            self._wait_timeframe = None

    def alive(self):
        return self._api.heartbeat()

    def start(self, size=100):
        for data in self.datas:
            data.next(size=size, tick=self._tick)

    def next(self):
        if self._tick > 0:
            time.sleep(self._wait_duration())
        for data in self.datas:
            data.next(tick=self._tick)

    def _wait_duration(self) -> float:
        now = datetime.now()
        delta = self._wait_timeframe.ceil(now) - now
        return delta.total_seconds()

    ### Extend
    def data_new(self, **kwargs):
        return self._data_cls(api=self._api, **kwargs)

    def markets(self, search=None):
        return self._api.markets(search=search)

    @classmethod
    def instance(
        cls,
        api: Optional[LiveAPI] = None,
        api_kwargs: Optional[dict] = None,
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
