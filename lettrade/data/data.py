import logging
import math
import re
from typing import Optional

import pandas as pd

logger = logging.getLogger(__name__)
_data_name_pattern = re.compile(r"^[\w\_]+$")

TIMEFRAME_STR_2_DELTA = {
    "1m": pd.Timedelta(minutes=1),
    "2m": pd.Timedelta(minutes=2),
    "3m": pd.Timedelta(minutes=3),
    "4m": pd.Timedelta(minutes=4),
    "5m": pd.Timedelta(minutes=5),
    "6m": pd.Timedelta(minutes=6),
    "10m": pd.Timedelta(minutes=10),
    "12m": pd.Timedelta(minutes=12),
    "15m": pd.Timedelta(minutes=15),
    "20m": pd.Timedelta(minutes=20),
    "30m": pd.Timedelta(minutes=30),
    "1h": pd.Timedelta(hours=1),
    "2h": pd.Timedelta(hours=2),
    "3h": pd.Timedelta(hours=3),
    "4h": pd.Timedelta(hours=4),
    "6h": pd.Timedelta(hours=6),
    "8h": pd.Timedelta(hours=8),
    "12h": pd.Timedelta(hours=12),
    "1d": pd.Timedelta(days=1),
    "1w": pd.Timedelta(weeks=1),
    # "1mn": pd.Timedelta(days=30),
}
TIMEFRAME_DELTA_2_STR = {v: k for k, v in TIMEFRAME_STR_2_DELTA.items()}


class TimeFrame(pd.Timedelta):
    _str: str

    def __new__(cls, tf: str | pd.Timedelta) -> None:
        if isinstance(tf, str):
            string = tf
            delta = TIMEFRAME_STR_2_DELTA[tf]
        elif isinstance(tf, pd.Timedelta):
            delta = tf
            string = TIMEFRAME_DELTA_2_STR[tf]
        elif isinstance(tf, int):
            delta = pd.Timedelta(minutes=tf)
            string = TIMEFRAME_DELTA_2_STR[tf]
        elif isinstance(tf, cls.__class__):
            string = tf._str
            delta = tf._delta
        else:
            raise RuntimeError("Timeframe %s is invalid format", tf)

        delta.__class__ = cls
        setattr(delta, "_str", string)
        return delta

    def string(self):
        return self._str

    def start_of(self, at: pd.Timestamp):
        seconds = self.total_seconds()

        if seconds < 60:  # Seconds
            raise NotImplementedError("TimeFrame seconds is not implement yet")

        if seconds < 60 * 60:  # Minutes
            begin = at.replace(minute=0, second=0, microsecond=0)
        elif seconds < 24 * 60 * 60:  # Hours
            begin = at.replace(hour=0, minute=0, second=0, microsecond=0)
        elif seconds < 7 * 24 * 60 * 60:  # Days
            begin = at.replace(day=0, hour=0, minute=0, second=0, microsecond=0)
        else:
            raise NotImplementedError(f"TimeFrame {self} is not implement yet")

        step = math.floor((at - begin) / self)
        return begin + step * self


class DataFeedIndex(pd.DatetimeIndex):
    _pointer: int = 0

    def __getitem__(self, value):
        if isinstance(value, int):
            # logger.warning("[TEST] DataFeedIndex.__getitem__ %s", value)
            return super().__getitem__(self._pointer + value)
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
        logger.warning("[TEST] DataFeedIndex._cmp_method %s %s", other, op)
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
