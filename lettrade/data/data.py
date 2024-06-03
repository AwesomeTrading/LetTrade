import logging
import re
from typing import Optional

import pandas as pd

from .inject import DataFrameInject
from .timeframe import TimeFrame

logger = logging.getLogger(__name__)

_data_name_pattern = re.compile(r"^[\w\_]+$")


class DataFeed(pd.DataFrame):
    """Data for Strategy. A implement of pandas.DataFrame"""

    l: DataFrameInject

    def __init__(
        self,
        *args,
        name: str,
        timeframe: TimeFrame,
        meta: Optional[dict] = None,
        **kwargs,
    ) -> None:
        """_summary_

        Args:
            name (str): _description_
            timeframe (TimeFrame): _description_
            meta (Optional[dict], optional): _description_. Defaults to None.

        Raises:
            RuntimeError: _description_
        """
        # Validate
        if not _data_name_pattern.match(name):
            raise RuntimeError(
                f"Bot name {name} is not valid format {_data_name_pattern}"
            )

        # Init
        super().__init__(*args, **kwargs)
        self._init_index()

        # Metadata
        if not meta:
            meta = dict()
        meta["name"] = name
        meta["timeframe"] = TimeFrame(timeframe)
        self.attrs = {"lt_meta": meta}

    # Internal
    def _init_index(self):
        if not isinstance(self.index, pd.DatetimeIndex):
            if not self.empty:
                raise RuntimeError("Index is not pandas.DatetimeIndex format")
            self.index = self.index.astype("datetime64[ns, UTC]")

        self.index.rename("datetime", inplace=True)

    def _set_main(self):
        """Set this dataframe is main datafeed"""
        self.meta["is_main"] = True

    # External
    def copy(self, deep=False, *args, **kwargs) -> "DataFeed":
        df = super().copy(deep=deep, *args, **kwargs)
        df = self.__class__(
            data=df,
            name=self.name,
            timeframe=self.timeframe,
            meta=self.meta.copy(),
        )
        return df

    def next(self, next=1):
        self.l.next(next)

    def bar(self, i=0) -> pd.Timestamp:
        return self.datetime.l[i]

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
