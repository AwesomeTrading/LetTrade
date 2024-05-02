import logging
from datetime import datetime

import pandas as pd

logger = logging.getLogger(__name__)


class DataFeedIndex(pd.Index):
    _data_cls = pd.DatetimeIndex
    _data: pd.DatetimeIndex
    _jump: int

    def __new__(cls, data):
        result = object.__new__(DataFeedIndex)
        result._data = data
        result._name = data._name
        result._references = data._references

        result._jump = 0
        return result

    # def _cmp_method(self, other, op):
    #     if isinstance(other, int):
    #         return self._jump > other

    #     return self._data._cmp_method(self, other, op)

    def __getitem__(self, i):
        if isinstance(i, int):
            return self._data[self._jump + i]
        return super().__getitem__(i)

    def next(self, size=1):
        self._jump += size

    def is_end(self):
        return self._jump >= self._data.size

    def _get_list_axis(self, *args, kwargs):
        return self._data._get_list_axis(*args, kwargs)


class DataFeed(pd.DataFrame):
    def __init__(
        self,
        name,
        # data: pd.DataFrame,
        meta={},
        # dtype={},
        *args,
        **kwargs,
    ) -> None:
        # dtype.update(
        #     {
        #         "datetime": "datetime64[ns, UTC]",
        #         "open": "float",
        #         "high": "float",
        #         "low": "float",
        #         "close": "float",
        #         "volume": "float",
        #     }
        # )
        # print(dtype)
        # data.set_index(
        #     pd.DatetimeIndex(data.datetime, dtype="datetime64[ns, UTC]"), inplace=True
        # )
        # print(data.index.tz_convert(pytz.utc))

        super().__init__(*args, **kwargs)
        # if not isinstance(self.index, pd.DatetimeIndex):
        #     self.index = data.index.tz_convert(pytz.utc)

        if not isinstance(self.index, DataFeedIndex):
            self.index = DataFeedIndex(data=self.index)
        # self.reset_index(inplace=True)

        # Metadata
        meta["name"] = name
        self.attrs = {"lt_meta": meta}

    def __getitem__(self, i):
        if isinstance(i, int):
            logger.warning("[TEST] DataFeed get item %s", i)
            return self.loc[i]
        return super().__getitem__(i)

    @property
    def meta(self):
        return self.attrs["meta"]

    @property
    def now(self) -> datetime:
        return self.datetime[0]

    @property
    def bar(self):
        return self.index
