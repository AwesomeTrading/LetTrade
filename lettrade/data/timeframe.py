import logging
import re

import pandas as pd

logger = logging.getLogger(__name__)


TIMEFRAME_UNIT_LET_2_PANDAS = {
    "s": "s",
    "m": "m",
    "h": "h",
    "d": "day",
    "w": "W",
    # "1mn"
}
TIMEFRAME_UNIT_PANDAS_2_LET = {v: k for k, v in TIMEFRAME_UNIT_LET_2_PANDAS.items()}

TIMEFRAME_DELTA_2_STR = {
    pd.Timedelta(1, "m"): (1, "m"),
    pd.Timedelta(2, "m"): (2, "m"),
    pd.Timedelta(3, "m"): (3, "m"),
    pd.Timedelta(4, "m"): (4, "m"),
    pd.Timedelta(5, "m"): (5, "m"),
    pd.Timedelta(6, "m"): (6, "m"),
    pd.Timedelta(10, "m"): (10, "m"),
    pd.Timedelta(12, "m"): (12, "m"),
    pd.Timedelta(15, "m"): (15, "m"),
    pd.Timedelta(20, "m"): (20, "m"),
    pd.Timedelta(30, "m"): (30, "m"),
    pd.Timedelta(1, "h"): (1, "h"),
    pd.Timedelta(2, "h"): (2, "h"),
    pd.Timedelta(3, "h"): (3, "h"),
    pd.Timedelta(4, "h"): (4, "h"),
    pd.Timedelta(6, "h"): (6, "h"),
    pd.Timedelta(8, "h"): (8, "h"),
    pd.Timedelta(12, "h"): (12, "h"),
    pd.Timedelta(1, "day"): (1, "d"),
    pd.Timedelta(1, "W"): (1, "w"),
    # "1mn": pd.Timedelta(days=30),
}

_pattern_timeframe_str = re.compile(f"^([0-9]+)([a-z]+)$")


class TimeFrame:
    delta: pd.Timedelta
    unit: str
    unit_pandas: str
    value: int

    def __init__(self, tf: str | pd.Timedelta) -> None:
        if isinstance(tf, TimeFrame):
            self.value = tf.value
            self.unit = tf.unit
        elif isinstance(tf, str):
            match = _pattern_timeframe_str.search(tf)
            if not match:
                raise RuntimeError(f"TimeFrame value {tf} is invalid")

            unit = match.group(2)
            if unit not in TIMEFRAME_UNIT_LET_2_PANDAS:
                raise RuntimeError(f"TimeFrame value {tf} with unit {unit} is invalid")

            self.value = int(match.group(1))
            self.unit = unit
        elif isinstance(tf, int):
            self.value = tf
            self.unit = "m"
        elif isinstance(tf, list):
            self.value = int(tf[0])
            self.unit = tf[1]
        elif isinstance(tf, pd.Timedelta):
            map = TIMEFRAME_DELTA_2_STR[tf]
            self.value = map[0]
            self.unit = map[1]
        else:
            raise RuntimeError(f"Timeframe {tf} is invalid format")

        # Setup
        self.unit_pandas = TIMEFRAME_UNIT_LET_2_PANDAS[self.unit]
        self.delta = pd.Timedelta(self.value, self.unit_pandas)

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
        freq = self.string_pandas
        if self.unit == "m":
            freq += "in"
        return at.ceil(freq=freq)
