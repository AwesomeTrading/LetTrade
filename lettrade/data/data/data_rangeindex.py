import logging

import pandas as pd

from .base import BaseDataFeed

logger = logging.getLogger(__name__)


class DataFeedIndex(pd.RangeIndex):
    def _next(self, next=1):
        self._range = range(self._range.start - next, self._range.stop - next)

    def _go_start(self):
        self._range = range(0, len(self._values))

    def _go_stop(self):
        self._range = range(-len(self._values) + 1, 1)

    def at(self, index: int):
        return self._values[index]


class DataFeed(BaseDataFeed):
    """Data for Strategy. A implement of pandas.DataFrame"""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(
            *args,
            **kwargs,
            columns=["datetime", "open", "high", "low", "close", "volume"],
        )
        self._init_index()

    def _init_index(self):
        if not isinstance(self.index, pd.RangeIndex):
            self.reset_index(inplace=True)

        self.index.__class__ = DataFeedIndex
        self.pointer_go_start()

    def __getitem__(self, i):
        if isinstance(i, int):
            # logger.warning("[TEST] DataFeed get item %s", i)
            return self.loc[i]
        return super().__getitem__(i)

    # Properties
    @property
    def now(self) -> pd.Timestamp:
        return self.datetime.loc[0]

    # Functions
    def bar(self, i=0) -> pd.Timestamp:
        return self.datetime.loc[i]

    def next(self, size=1) -> bool:
        self.index._next(size)

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

    def drop(self, *args, since=None, **kwargs):
        if since is None:
            return super().drop(*args, **kwargs)

        if isinstance(since, int):
            index = range(self.pointer_start, self.pointer_start + since)
            self.drop(index=index, inplace=True)
            self.reset_index(inplace=True)
            logger.info("BackTestDataFeed %s dropped %s rows", self.name, len(index))
            return

        raise RuntimeError(f"No implement to handle drop since {since}")

    # Pointer
    @property
    def pointer(self):
        return -self.index.start

    def pointer_go_start(self):
        self.index._go_start()

    def pointer_go_stop(self):
        self.index._go_stop()

    @property
    def pointer_start(self) -> int:
        return self.index.start

    @property
    def pointer_stop(self) -> int:
        return self.index.stop
