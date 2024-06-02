import logging

import pandas as pd

from .base import BaseDataFeed
from .inject import DataFrameInject

logger = logging.getLogger(__name__)


class DataFeed(BaseDataFeed):
    """Data for Strategy. A implement of pandas.DataFrame"""

    l: DataFrameInject

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._init_index()

    # Functions
    def _init_index(self):
        if not isinstance(self.index, pd.DatetimeIndex):
            if not self.empty:
                raise RuntimeError("Index is not pandas.DatetimeIndex format")
            self.index = self.index.astype("datetime64[ns, UTC]")

        self.index.rename("datetime", inplace=True)

    def copy(self, deep=False, *args, **kwargs) -> "DataFeed":
        df: "DataFeed" = super().copy(deep=deep, *args, **kwargs)
        # df.l_rebase()
        return df

    def next(self, next=1):
        self.l.next(next)

    def bar(self, i=0) -> pd.Timestamp:
        return self.datetime.l[i]

    def ibar(self, i=0) -> pd.Timestamp:
        return self.datetime.iloc[i]

    def push(self, rows: list):
        # cls = self.index.__class__
        for row in rows:
            dt = pd.to_datetime(row[0], unit="s")
            self.loc[
                dt,
                [
                    "open",
                    "high",
                    "low",
                    "close",
                    "volume",
                ],
            ] = [
                row[1],  # open
                row[2],  # high
                row[3],  # low
                row[4],  # close
                row[5],  # volume
            ]

        if __debug__:
            logger.info("[%s] New bar: \n%s", self.name, self.tail(len(rows)))

    def drop(self, *args, since=None, **kwargs):
        if since is None:
            return super().drop(*args, **kwargs)

        if isinstance(since, int):
            loc = self.index.l[since]
            index = self[self.index < loc].index
            super().drop(index=index, inplace=True)
            self.l.reset()
            logger.info("BackTestDataFeed %s dropped %s rows", self.name, len(index))
            return

        raise RuntimeError(f"No implement to handle drop since {since}")

    # Properties
    @property
    def datetime(self) -> pd.DatetimeIndex:
        return self.index

    @property
    def now(self) -> pd.Timestamp:
        return self.datetime.l[0]
