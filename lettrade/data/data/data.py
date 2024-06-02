import logging

import pandas as pd

from .base import BaseDataFeed

logger = logging.getLogger(__name__)


class IndexInject:
    _ats: list[int]
    _index: pd.DatetimeIndex

    def __init__(self, index) -> None:
        if not isinstance(index, pd.DatetimeIndex):
            raise RuntimeError("Index is not instance of pd.DatetimeIndex")

        if not hasattr(index, "_lt_ats"):
            setattr(index, "_lt_ats", [0])
        self._ats = getattr(index, "_lt_ats")

        self._index = index

    def __getitem__(self, value):
        return self._index._values[value + self.pointer]

    # Function
    def next(self, next=0):
        self._ats[0] += next

    # Pointer
    @property
    def pointer(self):
        return self._ats[0]

    def go_start(self):
        self._ats[0] = 0

    def go_stop(self):
        self._ats[0] = len(self._index) - 1

    def reset(self, *args, **kwargs):
        self._ats[0] = 0

    @property
    def start(self) -> int:
        return -self._ats[0]

    @property
    def stop(self) -> int:
        return len(self._index) - self._ats[0]


class SeriesInject(IndexInject):
    _owner: pd.DatetimeIndex

    def __init__(self, owner: pd.Series) -> None:
        super().__init__(index=owner.index)
        self._owner = owner

    def __getitem__(self, value):
        return self._owner._values[value + self.pointer]


class DataFrameInject(IndexInject):
    _owner: pd.DatetimeIndex

    def __init__(self, owner: pd.DataFrame) -> None:
        super().__init__(index=owner.index)
        self._owner = owner

    def __getitem__(self, value):
        return self._owner.iloc[value + self.pointer]


@property
def _lt_obj(self):
    if not hasattr(self, "_lt_inject"):
        if isinstance(self, pd.DataFrame):
            inject = DataFrameInject(self)
        elif isinstance(self, pd.Series):
            inject = SeriesInject(self)
        if isinstance(self, pd.DatetimeIndex):
            inject = IndexInject(self)

        setattr(self, "_lt_inject", inject)
        self.__dict__["l"] = inject

    # print("call inject")
    return self._lt_inject


# def _lt_obj_rebase(self):
#     if hasattr(self, "_lt_inject"):
#         delattr(self, "_lt_inject")


setattr(pd.DataFrame, "l", _lt_obj)
setattr(pd.Series, "l", _lt_obj)
setattr(pd.DatetimeIndex, "l", _lt_obj)

# setattr(pd.DataFrame, "l_rebase", _lt_obj_rebase)
# setattr(pd.Series, "l_rebase", _lt_obj_rebase)
# setattr(pd.DatetimeIndex, "l_rebase", _lt_obj_rebase)


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
