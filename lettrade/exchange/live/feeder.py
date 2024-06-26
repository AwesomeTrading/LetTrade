import time
from datetime import datetime

from lettrade.data import DataFeeder, TimeFrame

from .api import LiveAPI
from .data import LiveDataFeed


class LiveDataFeeder(DataFeeder):
    # Class properties
    _api_cls: type[LiveAPI] = LiveAPI
    _data_cls: type[LiveDataFeed] = LiveDataFeed

    # Object properties
    datas: list[LiveDataFeed]
    data: LiveDataFeed

    _api: LiveAPI
    _tick: bool
    _start_size: int
    _config: dict
    _wait_timeframe: TimeFrame

    def __init__(
        self,
        api: LiveAPI,
        tick: bool = 5,
        start_size: int = 500,
        **kwargs,
    ) -> None:
        """
        tick:
            tick < 0: no tick, just get completed bar
            tick == 0: wait until new bar change value
            tick > 0: sleep tick time (in seconds) then update
        """
        super().__init__()
        self._api = api
        self._tick = tick
        self._start_size = start_size
        self._config = kwargs

        if isinstance(self._tick, int):
            self._wait_timeframe = TimeFrame(f"{self._tick}s")
        else:
            self._wait_timeframe = None

    def alive(self):
        return self._api.heartbeat()

    def start(self):
        for data in self.datas:
            data.next(size=self._start_size, tick=self._tick)

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
        api: LiveAPI | None = None,
        api_kwargs: dict | None = None,
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
