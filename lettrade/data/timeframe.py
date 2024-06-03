import logging

import pandas as pd

logger = logging.getLogger(__name__)

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
