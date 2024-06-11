import logging
import re
from typing import Optional

import pandas as pd

from .timeframe import TimeFrame
from .wrapper import LetDataFeedWrapper

logger = logging.getLogger(__name__)

_data_name_pattern = re.compile(r"^[\w\_]+$")


class DataFeed(pd.DataFrame):
    """Data for Strategy. A implement of pandas.DataFrame"""

    l: LetDataFeedWrapper

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

        # LetWrapper
        object.__setattr__(self, "l", LetDataFeedWrapper(self))

    def __setstate__(self, data):
        super().__setstate__(data)
        if not hasattr(self, "l"):
            object.__setattr__(self, "l", LetDataFeedWrapper(self))

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
    def copy(self, deep: bool = False, **kwargs) -> "DataFeed":
        df = super().copy(deep=deep)
        df = self.__class__(
            data=df,
            name=self.name,
            timeframe=self.timeframe,
            meta=self.meta.copy(),
            **kwargs,
        )
        return df

    def next(self, size=1):
        self.l.next(size)

    def bar(self, i=0) -> pd.Timestamp:
        return self.l.index[i]

    def push(self, rows: list):
        for row in rows:
            dt = pd.to_datetime(row[0], unit="s", utc=True)
            self.at[
                dt,
                (
                    "open",
                    "high",
                    "low",
                    "close",
                    "volume",
                ),
            ] = (
                row[1],  # open
                row[2],  # high
                row[3],  # low
                row[4],  # close
                row[5],  # volume
            )

        if __debug__:
            logger.info("[%s] Update bar: \n%s", self.name, self.tail(len(rows)))

    def drop(self, *args, since=None, **kwargs):
        if since is None:
            return super().drop(*args, **kwargs)

        if isinstance(since, int):
            loc = self.l.index[since]
        elif isinstance(since, str):
            loc = pd.Timestamp(since)
        elif isinstance(since, pd.Timestamp):
            loc = since
        else:
            raise RuntimeError(f"DataFeed.drop since {since} is invalid")

        index = self[self.index < loc].index
        super().drop(index=index, inplace=True)
        self.l.reset()
        logger.info("BackTestDataFeed %s dropped %s rows", self.name, len(index))

    # Properties
    # @property
    # def datetime(self) -> pd.DatetimeIndex:
    #     return self.index

    @property
    def now(self) -> pd.Timestamp:
        return self.l.index[0]

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


if __debug__:
    # __debug__ code willbe remove when run in python production flag `python -O` or `python -OO`
    from lettrade.base.flag import validate_data_getitem_pointer

    if validate_data_getitem_pointer:
        # Check missing data get item by pointer:
        # Wrong: data.index[<pointer>] -> Right: data.l.index[<pointer>]
        # Wrong: data.open[<pointer>] -> Right: data.l.open[<pointer>]

        import logging

        logger = logging.getLogger(__name__)

        def inject_data_validator(cls):
            # __class__ = cls

            def data_getitem(self, value):
                if isinstance(value, int):
                    logger.warning(
                        "[%s] Get data by pointer %d many wrong data. "
                        "using <data>.l[<pointer>] to get data at pointer",
                        self.__class__,
                        value,
                    )
                return self.__my__getitem__(value)

            cls.__my__getitem__ = cls.__getitem__
            cls.__getitem__ = data_getitem

        inject_data_validator(DataFeed)
        inject_data_validator(pd.Series)
        inject_data_validator(pd.DatetimeIndex)
