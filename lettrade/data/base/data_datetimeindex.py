import logging
from typing import Optional, final

import numpy as np
import pandas as pd

from .base import DataFeedBase, TimeFrame

logger = logging.getLogger(__name__)


########## Pandas Hack ##########
class DataFeedIndex(pd.DatetimeIndex):
    _lt_pointers: list[int] = [0]

    def __getitem__(self, value):
        if isinstance(value, int):
            # logger.warning("[TEST] DataFeedIndex.__getitem__ %s", value)
            value += self.pointer
        return super().__getitem__(value)

    def get_loc(self, key, *args, **kwargs):
        if isinstance(key, int):
            # logger.warning("[TEST] DataFeedIndex.get_loc %s", key)
            return key + self.pointer
        return super().get_loc(key) - self.pointer

    @property
    def pointer(self):
        return self._lt_pointers[0]

    @property
    def _should_fallback_to_positional(self):
        return False

    def at(self, index: int):
        return self._values[index]

    def _cmp_method(self, other, op):
        if isinstance(other, int):
            other = self._values[other + self.pointer]

        if __debug__:
            logger.warning(
                "[TEST] DataFeedIndex._cmp_method other=%s, operator=%s",
                other,
                op,
            )

        return super()._cmp_method(other, op)


class DateTimeIndexDataFeed(DataFeedBase):
    """Data for Strategy. A implement of pandas.DataFrame"""

    _lt_pointers: list[int] = [0]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._init_index()

    def _init_index(self):
        if not isinstance(self.index, pd.DatetimeIndex):
            if not self.empty:
                raise RuntimeError("Index is not pandas.DatetimeIndex format")
            self.index = self.index.astype("datetime64[ns, UTC]")

        self.index.rename("datetime", inplace=True)

        self.index.__class__ = DataFeedIndex
        self._rebase_pointer()

    def copy(self, deep=False, *args, **kwargs) -> "DataFeed":
        df = super().copy(deep=deep, *args, **kwargs)
        df._rebase_pointer()
        return df

    # Properties
    @property
    def datetime(self) -> pd.DatetimeIndex:
        return self.index

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
        return self.datetime._values[self.pointer]

    # Functions
    def bar(self, i=0) -> pd.Timestamp:
        return self.datetime._values[self.pointer + i]

    def _set_main(self):
        """Set this dataframe is main datafeed"""
        self.meta["is_main"] = True

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
        self.index.__class__ = DataFeedIndex

        if __debug__:
            logger.info("[%s] New bar: \n%s", self.name, self.tail(1))

    # Pointer
    @property
    def pointer(self):
        return self._lt_pointers[0]

    def next(self, next=1):
        self._lt_pointers[0] += next

    def go_start(self):
        self._lt_pointers[0] = 0

    def go_stop(self):
        self._lt_pointers[0] = len(self) - 1

    def _rebase_pointer(self):
        self._lt_pointers = [0]
        self.index._lt_pointers = self._lt_pointers

    @property
    def start(self) -> int:
        return -self._lt_pointers[0]

    @property
    def stop(self) -> int:
        return len(self) - self._lt_pointers[0]

    ########## Pandas Hack ##########
    @final
    def __getitem__(self, i):
        if isinstance(i, int):
            # logger.warning("[TEST] DataFeed get item %s", i)
            return self.iloc[i]
        return super().__getitem__(i)

    def _get_value(self, index, col, takeable: bool = False) -> "Scalar":
        if isinstance(index, int):
            index = self.index._values[index + self.pointer]
        return super()._get_value(index, col, takeable)

    def _ixs(self, i: int, axis: 0) -> pd.Series:
        # TODO: PATCH return
        if axis == 0:
            i += self.pointer
            new_mgr = self._mgr.fast_xs(i)

            # if we are a copy, mark as such
            copy = isinstance(new_mgr.array, np.ndarray) and new_mgr.array.base is None
            result = self._constructor_sliced_from_mgr(new_mgr, axes=new_mgr.axes)
            result._name = self.index._values[i]
            result = result.__finalize__(self)
            result._set_is_copy(self, copy=copy)
            return result

        return super()._ixs(i, axis)

    @final
    def xs(self, key, axis=0, *args, **kwargs):
        if axis == 0:
            if isinstance(key, (pd.Timestamp, int)):
                if isinstance(key, pd.Timestamp):
                    loc = self.index.get_loc(key)
                    loc += self.pointer
                elif isinstance(key, int):
                    loc = key

                new_mgr = self._mgr.fast_xs(loc)

                result = self._constructor_sliced_from_mgr(new_mgr, axes=new_mgr.axes)
                result._name = self.index._values[loc]
                result = result.__finalize__(self)
                result._set_is_copy(self, copy=not result._is_view)
                return result

        super().xs(
            key,
            axis=0,
            *args,
            **kwargs,
        )
