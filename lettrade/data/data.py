import logging
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


class DataFeedIndex(pd.RangeIndex):
    def next(self, next=1):
        self._range = range(self._range.start - next, self._range.stop - next)

    def go_start(self):
        self._range = range(0, len(self._values))

    def go_stop(self):
        self._range = range(-len(self._values) + 1, 1)

    def at(self, index: int):
        return self._values[index]


class DataFeed(pd.DataFrame):
    """Data for Strategy. A implement of pandas.DataFrame"""

    def __init__(
        self,
        *args,
        name: str,
        # data: pd.DataFrame,
        timeframe: TimeFrame,
        meta: Optional[dict] = None,
        # dtype: list[tuple] = [],
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
                f"Bot name {name} is not valid format {_data_name_pattern}"
            )

        super().__init__(*args, **kwargs)
        if isinstance(self.index, pd.DatetimeIndex):
            self.reset_index(inplace=True)
        #     if not self.empty:
        #         raise RuntimeError("Index is not pandas.DatetimeIndex format")
        #     self.index = self.index.astype("datetime64[ns, UTC]")

        if not isinstance(self.index, pd.RangeIndex):
            self.reset_index(inplace=True)
            # self.index = pd.RangeIndex(start=0, stop=len(self.index), step=1)

        self.index.__class__ = DataFeedIndex
        # self.index.go_start()

        # Metadata
        if not meta:
            meta = dict()
        meta["name"] = name
        meta["timeframe"] = TimeFrame(timeframe)
        self.attrs = {"lt_meta": meta}

    def __getitem__(self, i):
        if isinstance(i, int):
            # logger.warning("[TEST] DataFeed get item %s", i)
            return self.loc[i]
        return super().__getitem__(i)

    def copy(self, deep=False, *args, **kwargs) -> "DataFeed":
        df = super().copy(deep=deep, *args, **kwargs)
        df = self.__class__(data=df, name=self.name, timeframe=self.timeframe)
        return df

    # Properties
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
    def now(self) -> pd.Timestamp:
        return self.datetime.loc[0]

    # Functions
    def bar(self, i=0) -> pd.Timestamp:
        return self.datetime.loc[i]

    def next(self, size=1) -> bool:
        raise NotImplementedError("Method is not implement yet")

    # def append(self, index, columns, row):
    #     df = pd.DataFrame()
    #     self.loc[
    #         index,
    #         columns,
    #     ] = [
    #         row[1],  # open
    #         row[2],  # high
    #         row[3],  # low
    #         row[4],  # close
    #         row[5],  # volume
    #     ]

    def _set_main(self):
        """Set this dataframe is main datafeed"""
        self.meta["is_main"] = True

    def push(self, rows: list):
        if len(rows) == 0:
            return

        if self.empty:
            i_start = 0
        else:
            i_start = -len(rows) + 1

        for i, row in enumerate(rows):
            dt = pd.to_datetime(row[0], unit="s")
            self.loc[
                i_start + i,
                [
                    "datetime",
                    "open",
                    "high",
                    "low",
                    "close",
                    "volume",
                ],
            ] = [
                dt,
                row[1],  # open
                row[2],  # high
                row[3],  # low
                row[4],  # close
                row[5],  # volume
            ]
        self.index = DataFeedIndex(-len(self.index) + 1, 1)

        if __debug__:
            logger.info("[%s] New bar: \n%s", self.name, self.tail(1))
