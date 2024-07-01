import logging
import re
from typing import TYPE_CHECKING, Callable

import pandas as pd

from .timeframe import TimeFrame
from .wrapper import LetDataFeedWrapper

if TYPE_CHECKING:
    from lettrade import indicator

logger = logging.getLogger(__name__)

_data_name_pattern = re.compile(r"^[\w\_]+$")


class DataFeed(pd.DataFrame):
    """Data for Strategy. A implement of pandas.DataFrame"""

    l: LetDataFeedWrapper
    """LetTrade DataFeed wrapper using to manage index pointer of DataFeed"""

    def __init__(
        self,
        *args,
        name: str,
        timeframe: TimeFrame,
        meta: dict | None = None,
        **kwargs,
    ) -> None:
        """_summary_

        Args:
            name (str): _description_
            timeframe (TimeFrame): _description_
            meta (dict | None, optional): _description_. Defaults to None.

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
        """_summary_

        Args:
            deep (bool, optional): _description_. Defaults to False.

        Returns:
            DataFeed: _description_
        """
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
        """Load next data

        Args:
            size (int, optional): _description_. Defaults to 1.
        """
        self.l.next(size)

    def bar(self, i: int = 0) -> pd.Timestamp:
        """Get current pd.Timestamp value of DataFeed

        Args:
            i (int, optional): Index. Defaults to 0.

        Returns:
            pd.Timestamp: _description_
        """
        return self.l.index[i]

    def push(
        self,
        rows: list[list[int | float]],
        unit: str | None = None,
        utc: bool = True,
        **kwargs,
    ):
        """Push new rows to DataFeed

        Args:
            rows (list[list[int | float]]): list of rows `[["timestamp", "open price", "high price"...]]`
            unit (str | None, optional): pandas.Timestamp parsing unit. Defaults to None.
            utc (bool, optional): _description_. Defaults to True.
        """
        for row in rows:
            dt = pd.to_datetime(row[0], unit=unit, utc=utc, **kwargs)
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
            logger.debug("[%s] Update bar: \n%s", self.name, self.tail(len(rows)))

    def drop(
        self,
        *args,
        since: int | str | pd.Timestamp | None = None,
        to: int | str | pd.Timestamp | None = None,
        **kwargs,
    ) -> None:
        """_summary_

        Args:
            since (int | str | pd.Timestamp | None, optional): _description_. Defaults to None.
            to (int | str | pd.Timestamp | None, optional): _description_. Defaults to None.

        Raises:
            RuntimeError: _description_
        """
        if since is None and to is None:
            super().drop(*args, **kwargs)
            return

        condiction = None

        # Since
        if since is not None:
            if isinstance(since, int):
                loc = self.l.index[since]
            elif isinstance(since, str):
                loc = pd.to_datetime(since, utc=True)
            elif isinstance(since, pd.Timestamp):
                loc = since
            else:
                raise RuntimeError(f"DataFeed.drop since {since} is invalid")
            condiction = self.index < loc

        # To
        if to is not None:
            if isinstance(to, int):
                loc = self.l.index[to]
            elif isinstance(to, str):
                loc = pd.to_datetime(to, utc=True)
            elif isinstance(to, pd.Timestamp):
                loc = to
            else:
                raise RuntimeError(f"DataFeed.drop to {to} is invalid")

            if condiction is None:
                condiction = self.index > loc
            else:
                condiction = condiction | (self.index > loc)

        index = self[condiction].index
        super().drop(index=index, inplace=True)
        self.l.reset()

        if __debug__:
            logger.debug("BackTestDataFeed %s dropped %s rows", self.name, len(index))

    @property
    def now(self) -> pd.Timestamp:
        """Property to get current index value of DataFeed"""
        return self.l.index[0]

    @property
    def meta(self) -> dict:
        """Property to get metadata of DataFeed"""
        return self.attrs["lt_meta"]

    @property
    def name(self) -> str:
        """Property to get name of DataFeed"""
        return self.meta["name"]

    @property
    def timeframe(self) -> TimeFrame:
        """Property to get timeframe of DataFeed"""
        return self.meta["timeframe"]

    @property
    def is_main(self) -> bool:
        """Property to check DataFeed is main DataFeed or not"""
        return self.meta.get("is_main", False)

    @property
    def i(self) -> "indicator":
        """Alias to `lettrade.indicator` and using in DataFeed by call: `DataFeed.i.indicator_name()`"""
        if not hasattr(self, "_lt_indicators_injector"):
            object.__setattr__(
                self,
                "_lt_indicators_injector",
                _LetIndicatorsInjector(self),
            )
        return self._lt_indicators_injector


class _LetIndicatorsInjector:
    """Class help to inject indicator into pandas.DataFrame with prefix `_lt_i_`.
    Avoid conflic between pandas.DataFrame column name and indicator function name
    """

    def __init__(self, df: DataFeed) -> None:
        self.__dict__["df"] = df

        from lettrade import indicator

        indicator.indicators_inject_pandas(self)

    def __setattr__(self, name: str, value: Callable) -> None:
        from pandas.core.base import PandasObject

        i_name = f"_lt_i_{name}"
        if hasattr(PandasObject, i_name):
            raise RuntimeError(f"Indicator {i_name} existed")

        setattr(PandasObject, i_name, value)

    def __getattr__(self, name: str) -> Callable:
        return getattr(self.__dict__["df"], f"_lt_i_{name}")


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
                return self.__lt__getitem__(value)

            cls.__lt__getitem__ = cls.__getitem__
            cls.__getitem__ = data_getitem

        inject_data_validator(DataFeed)
        inject_data_validator(pd.Series)
        inject_data_validator(pd.DatetimeIndex)
