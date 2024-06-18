import logging
import re
from datetime import datetime

import pandas as pd
from typing_extensions import Self

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

_pattern_timeframe_str = re.compile(r"^([0-9]+)([a-z]+)$")


class TimeFrame:
    """DataFeed TimeFrame"""

    delta: pd.Timedelta
    unit: str
    unit_pandas: str
    value: int

    def __init__(self, tf: int | str | list | pd.Timedelta | Self) -> None:
        """_summary_

        Args:
            tf (int | str | list | pd.Timedelta | TimeFrame):
                - `int`: TimeFrame in minutes. Example: TimeFrame(5) == TimeFrame("5m")
                - `str`: string format of TimeFrame in `s`, `m`, `h`, `d`, `w`.
        Raises:
            RuntimeError: _description_
        """
        if isinstance(tf, TimeFrame):
            self.value = tf.value
            self.unit = tf.unit
        elif isinstance(tf, str):
            match = _pattern_timeframe_str.search(tf)
            if not match:
                raise RuntimeError(f"TimeFrame value {tf} is invalid")

            self.value = int(match.group(1))
            self.unit = match.group(2)
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

        # Validate
        self._validate()

        # Setup
        self.unit_pandas = TIMEFRAME_UNIT_LET_2_PANDAS[self.unit]
        self.delta = pd.Timedelta(self.value, self.unit_pandas)

        # Warning
        if self.delta not in TIMEFRAME_DELTA_2_STR:
            if self.unit not in ["s", "m"]:
                logger.warning(
                    "Unsupport TimeFrame(%s), some function may not work floor()/ceil()...",
                    self.delta,
                )

    def _validate(self):
        # Unit
        if self.unit not in TIMEFRAME_UNIT_LET_2_PANDAS:
            raise RuntimeError(f"TimeFrame unit {self.unit} is invalid")

        # Value
        if self.value <= 0:
            raise RuntimeError(f"Timeframe value {self.value} is <= 0")
        elif self.unit in ["s", "m"] and self.value >= 60:
            raise RuntimeError(f"Timeframe value {self.value} is >= 60{self.unit}")
        elif self.unit == "h" and self.value >= 24:
            raise RuntimeError(f"Timeframe value {self.value} is >= 24h")
        elif self.unit == "d" and self.value >= 7:
            raise RuntimeError(f"Timeframe value {self.value} is >= 7d")

    def __repr__(self) -> str:
        return self.string

    @property
    def string(self):
        return f"{self.value}{self.unit}"

    @property
    def string_pandas(self):
        return f"{self.value}{self.unit_pandas}"

    def floor(self, at: datetime | pd.Timestamp):
        if isinstance(at, datetime):
            at = pd.Timestamp(at)

        freq = self.string_pandas
        if self.unit == "m":
            freq += "in"
        return at.floor(freq=freq)

    def ceil(self, at: datetime | pd.Timestamp):
        if isinstance(at, datetime):
            at = pd.Timestamp(at)

        freq = self.string_pandas
        if self.unit == "m":
            freq += "in"
        return at.ceil(freq=freq)
