import logging
import math
import re
from typing import Optional

import pandas as pd

logger = logging.getLogger(__name__)
_data_name_pattern = re.compile(r"^[\w\_]+$")

TIMEFRAME_STR_2_DELTA = {
    "1m": (1, "m", "m", pd.Timedelta(1, "m")),
    "2m": (2, "m", "m", pd.Timedelta(2, "m")),
    "3m": (3, "m", "m", pd.Timedelta(3, "m")),
    "4m": (4, "m", "m", pd.Timedelta(4, "m")),
    "5m": (5, "m", "m", pd.Timedelta(5, "m")),
    "6m": (6, "m", "m", pd.Timedelta(6, "m")),
    "10m": (10, "m", "m", pd.Timedelta(10, "m")),
    "12m": (12, "m", "m", pd.Timedelta(12, "m")),
    "15m": (15, "m", "m", pd.Timedelta(15, "m")),
    "20m": (20, "m", "m", pd.Timedelta(20, "m")),
    "30m": (30, "m", "m", pd.Timedelta(30, "m")),
    "1h": (1, "h", "h", pd.Timedelta(1, "h")),
    "2h": (2, "h", "h", pd.Timedelta(2, "h")),
    "3h": (3, "h", "h", pd.Timedelta(3, "h")),
    "4h": (4, "h", "h", pd.Timedelta(4, "h")),
    "6h": (6, "h", "h", pd.Timedelta(6, "h")),
    "8h": (8, "h", "h", pd.Timedelta(8, "h")),
    "12h": (12, "h", "h", pd.Timedelta(12, "h")),
    "1d": (1, "d", "day", pd.Timedelta(1, "day")),
    "1w": (1, "w", "W", pd.Timedelta(1, "W")),
    # "1mn": pd.Timedelta(days=30),
}
TIMEFRAME_DELTA_2_STR = {
    v[3]: [v[0], v[1], v[2], k] for k, v in TIMEFRAME_STR_2_DELTA.items()
}


class TimeFrame:
    delta: pd.Timedelta
    unit: str
    unit_pandas: str
    value: int

    def __init__(self, tf: str | pd.Timedelta) -> None:
        if isinstance(tf, TimeFrame):
            self.delta = tf.delta
            self.unit = tf.unit
            self.unit_pandas = tf.unit_pandas
            self.value = tf.value
        elif isinstance(tf, str):
            map = TIMEFRAME_STR_2_DELTA[tf]
            self.value = map[0]
            self.unit = map[1]
            self.unit_pandas = map[2]
            self.delta = pd.Timedelta(map[3])
        elif isinstance(tf, int):
            map = TIMEFRAME_STR_2_DELTA[f"{tf}m"]
            self.value = map[0]
            self.unit = map[1]
            self.unit_pandas = map[2]
            self.delta = pd.Timedelta(map[3])
        elif isinstance(tf, pd.Timedelta):
            map = TIMEFRAME_DELTA_2_STR[tf]
            self.value = map[0]
            self.unit = map[1]
            self.unit_pandas = map[2]
            self.delta = pd.Timedelta(tf)
        else:
            raise RuntimeError(f"Timeframe {tf} is invalid format")

    def __repr__(self) -> str:
        return self.string

    @property
    def string(self):
        return f"{self.value}{self.unit}"

    @property
    def string_pandas(self):
        return f"{self.value}{self.unit_pandas}"

    def floor(self, at: pd.Timestamp):
        freq = self.string_pandas
        if self.unit == "m":
            freq += "in"
        return at.floor(freq=freq)

    def ceil(self, at: pd.Timestamp):
        return at.ceil(freq=self.string_pandas)


# _timeframe_foramt = re.compile(r"^(\d+)(\w+)$")
# class TimeFrame(pd.Timedelta):
#     _tf_value: int
#     _tf_unit: str

#     def __new__(cls, tf: str | pd.Timedelta) -> None:
#         if isinstance(tf, str):
#             string = tf
#             delta = TIMEFRAME_STR_2_DELTA[tf]
#         elif isinstance(tf, pd.Timedelta):
#             delta = tf
#             string = TIMEFRAME_DELTA_2_STR[tf]
#         elif isinstance(tf, int):
#             delta = pd.Timedelta(tf, unit="m")
#             string = TIMEFRAME_DELTA_2_STR[tf]
#         elif isinstance(tf, cls.__class__):
#             string = tf.string()
#             delta = tf
#         else:
#             raise RuntimeError("Timeframe %s is invalid format", tf)

#         # # Parse unit
#         # if delta.unit == "ns":
#         #     seconds = delta.total_seconds()
#         #     if seconds < 60:  # Seconds
#         #         raise NotImplementedError("TimeFrame seconds is not implement yet")
#         #     if seconds < 60 * 60:  # Minutes
#         #         minutes = math.floor(seconds / 60)
#         #         delta = pd.Timedelta(minutes, unit="m")
#         #     elif seconds < 24 * 60 * 60:  # Hours
#         #         hours = math.floor(seconds / (60 * 60))
#         #         delta = pd.Timedelta(hours, unit="h")
#         #     elif seconds < 7 * 24 * 60 * 60:  # Days
#         #         hours = math.floor(seconds / (24 * 60 * 60))
#         #         delta = pd.Timedelta(hours, unit="day")
#         #     elif seconds == 7 * 24 * 60 * 60:  # Days
#         #         delta = pd.Timedelta(1, unit="W")
#         #     else:
#         #         raise NotImplementedError(f"TimeFrame {delta} is not implement yet")

#         searchs = _timeframe_foramt.search(string)
#         if not searchs:
#             raise RuntimeError(
#                 f"TimeFrame {string} is invalid format {_timeframe_foramt}"
#             )
#         value = int(searchs.group(1))
#         unit = searchs.group(2)

#         # Init object
#         delta = super().__new__(TimeFrame, delta)
#         delta.__class__ = cls

#         print("__new__", delta, type(delta))

#         setattr(delta, "_tf_value", value)
#         setattr(delta, "_tf_unit", unit)
#         return delta

#     def __init__(self, *args, **kwargs) -> None:
#         print("init", *args, **kwargs)
#         super().__init__()

#     def get_string(self, pandas=False):
#         return f"{self._tf_value}{self.get_unit(pandas=pandas)}"

#     def get_value(self):
#         return self._tf_value

#     def get_unit(self, pandas=False):
#         if pandas:
#             if self._tf_unit == "d":
#                 return "day"
#             if self._tf_unit == "w":
#                 return "W"
#         return self._tf_unit

#     def get_floor(self, at: pd.Timestamp):
#         # seconds = self.total_seconds()

#         # if seconds < 60:  # Seconds
#         #     raise NotImplementedError("TimeFrame seconds is not implement yet")

#         # if seconds < 60 * 60:  # Minutes
#         #     # begin = at.replace(minute=0, second=0, microsecond=0)
#         #     begin = at.floor(freq=self.get_string(pandas=True))
#         # elif seconds < 24 * 60 * 60:  # Hours
#         #     begin = at.replace(hour=0, minute=0, second=0, microsecond=0)
#         # elif seconds < 7 * 24 * 60 * 60:  # Days
#         #     begin = at.replace(day=0, hour=0, minute=0, second=0, microsecond=0)
#         # else:
#         #     raise NotImplementedError(f"TimeFrame {self} is not implement yet")

#         # step = math.floor((at - begin) / self)
#         # return begin + step * self

#         return at.floor(freq=self.get_string(pandas=True))

#     def get_ceil(self, at: pd.Timestamp):
#         # return self.floor(at) + self
#         return at.ceil(freq=self.get_string(pandas=True))

#     # Bypass pickle
#     def __copy__(self):
#         return self.__new__(TimeFrame, self)

#     def __deepcopy__(self, memo=None):
#         return self.__new__(TimeFrame, self)


class DataFeedIndex(pd.DatetimeIndex):
    _pointer: int = 0

    def __getitem__(self, value):
        if isinstance(value, int):
            # logger.warning("[TEST] DataFeedIndex.__getitem__ %s", value)
            # return super().__getitem__(self._pointer + value)
            value += self._pointer
        return super().__getitem__(value)

    def get_loc(self, key, *args, **kwargs):
        # logger.warning("[TEST] DataFeedIndex.get_loc %s", key)
        return key + self._pointer

    @property
    def pointer(self):
        return self._pointer

    def next(self, next=1):
        self._pointer += next

    @property
    def start(self) -> int:
        return -self._pointer

    @property
    def stop(self) -> int:
        return len(self._values) - self._pointer

    @property
    def _should_fallback_to_positional(self):
        return False

    def at(self, index: int):
        return self._values[index]

    def _cmp_method(self, other, op):
        if isinstance(other, int):
            other = self[other]
        logger.warning(
            "[TEST] DataFeedIndex._cmp_method other=%s, operator=%s",
            other,
            op,
        )
        return super()._cmp_method(other, op)


class DataFeed(pd.DataFrame):
    """Data for Strategy. A implement of pandas.DataFrame"""

    def __init__(
        self,
        *args,
        name: str,
        # data: pd.DataFrame,
        timeframe: TimeFrame,
        meta: Optional[dict] = None,
        # dtype={},
        **kwargs,
    ) -> None:
        """_summary_

        Args:
            name (str): Name of DataFeed
            meta (Optional[dict], optional): metadata of DataFeed. Defaults to None.
            *args (list): `pandas.DataFrame` list parameters
            **kwargs (dict): `pandas.DataFrame` dict parameters
        """
        # Validate
        if not _data_name_pattern.match(name):
            raise RuntimeError(
                "Bot name %s is not valid format %s",
                name,
                _data_name_pattern,
            )

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
        self.index.rename("datetime", inplace=True)
        self.index.__class__ = DataFeedIndex

        # if not isinstance(self.index, pd.RangeIndex):
        #     self.reset_index(inplace=True)
        # self.index = pd.RangeIndex(start=0, stop=len(self.index), step=1)

        # Metadata
        if not meta:
            meta = dict()
        meta["name"] = name
        meta["timeframe"] = TimeFrame(timeframe)
        self.attrs = {"lt_meta": meta}

    def __getitem__(self, i):
        if isinstance(i, int):
            logger.warning("[TEST] DataFeed get item %s", i)
            return self.loc[i]
        return super().__getitem__(i)

    def copy(self, deep=False, *args, **kwargs) -> "DataFeed":
        df = super().copy(deep=deep, *args, **kwargs)
        df = self.__class__(data=df, name=self.name, timeframe=self.timeframe)
        # df.reset_index(inplace=True)
        return df

    # Properties
    @property
    def datetime(self) -> pd.DatetimeIndex:
        return self.index

    @property
    def meta(self) -> dict:
        return self.attrs["lt_meta"]

    @property
    def name(self) -> str:
        return self.meta["name"]

    @property
    def timeframe(self) -> TimeFrame:
        return self.meta["timeframe"]

    @property
    def is_main(self) -> bool:
        return self.meta.get("is_main", False)

    @property
    def now(self) -> datetime:
        return self.index[0]

    # Functions
    def bar(self, i=0) -> datetime:
        return self.index[i]

    def next(self, size=1) -> bool:
        raise NotImplementedError("Method is not implement yet")

    def _set_main(self):
        """Set this dataframe is main datafeed"""
        self.meta["is_main"] = True
