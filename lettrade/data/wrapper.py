from typing import Any

import pandas as pd
from pandas.core.indexing import _iLocIndexer

__WRAPPER_KEY__ = "_lt_wrapper"


class ILocWrapper:
    _data: pd.DatetimeIndex
    _owner: "DataFeedWrapper"

    def __init__(self, data, owner) -> None:
        self._data = data
        self._owner = owner

    def __getattr__(self, name: str):
        if hasattr(self._data, name):
            return getattr(self._data, name)
        raise NotImplementedError(f"Method {name} is not implement yet")

    def __getitem__(self, item: int | slice):
        if isinstance(item, int):
            item += self.pointer
        if isinstance(item, slice):
            item = slice(
                item.start + self.pointer,
                item.stop + self.pointer,
                item.step,
            )
        return self._data[item]

    # Property
    @property
    def pointer(self):
        return self._owner.pointer


class IndexWapper:
    _data: pd.DatetimeIndex
    _owner: "DataFeedWrapper"

    def __init__(self, data, owner) -> None:
        self._data = data
        self._owner = owner

    def __getattr__(self, name: str):
        if hasattr(self._data, name):
            return getattr(self._data, name)
        raise NotImplementedError(f"Method {name} is not implement yet")

    def __getitem__(self, item: int | slice):
        if isinstance(item, int):
            item += self.pointer
        if isinstance(item, slice):
            item = slice(
                item.start + self.pointer,
                item.stop + self.pointer,
                item.step,
            )
        return self._data[item]

    # Property
    @property
    def pointer(self):
        return self._owner.pointer


class SeriesWapper:
    _data: pd.DatetimeIndex
    _owner: "DataFeedWrapper"
    _iloc: ILocWrapper

    def __init__(self, data, owner) -> None:
        self._data = data
        self._owner = owner
        self._iloc = ILocWrapper(self._data.iloc, self._owner)

    def __getattr__(self, name: str):
        if hasattr(self._data, name):
            return getattr(self._data, name)
        raise NotImplementedError(f"Method {name} is not implement yet")

    def __getitem__(self, item: int | slice | Any):
        if isinstance(item, (int, slice)):
            return self._iloc[item]
        return self._data[item]

    # Property
    @property
    def iloc(self) -> _iLocIndexer:
        return self._iloc

    @property
    def pointer(self):
        return self._owner.pointer


class DataFeedWrapper:
    _data: pd.DataFrame
    _pointer: int
    _iloc: ILocWrapper

    def __init__(self, data) -> None:
        self._pointer = 0
        self._data = data
        self._iloc = ILocWrapper(self._data.iloc, self)

    def __getattr__(
        self, name: str
    ) -> pd.Series | pd.DatetimeIndex | SeriesWapper | IndexWapper:
        if hasattr(self._data, name):
            result = getattr(self._data, name)

            # Exist
            if hasattr(result, __WRAPPER_KEY__):
                return getattr(result, __WRAPPER_KEY__)

            # Set wrapper
            if isinstance(result, pd.Series):
                wrapper = SeriesWapper(result, self)
                setattr(result, __WRAPPER_KEY__, wrapper)
                return wrapper

            if isinstance(result, pd.DatetimeIndex):
                wrapper = IndexWapper(result, self)
                setattr(result, __WRAPPER_KEY__, wrapper)
                return wrapper

            return result

        raise NotImplementedError(f"Method {name} is not implement yet")

    def __getitem__(self, item: int | slice):
        if isinstance(item, int):
            item += self.pointer
        if isinstance(item, slice):
            item = slice(
                item.start + self.pointer,
                item.stop + self.pointer,
                item.step,
            )
        return self._data.iloc[item]

    # Function
    def next(self, size=1):
        self._pointer += size

    # Property
    @property
    def iloc(self) -> _iLocIndexer:
        return self._iloc

    @property
    def pointer(self):
        return self._pointer


@property
def _lettrade_wrapper(self) -> DataFeedWrapper:
    if not hasattr(self, __WRAPPER_KEY__):
        object.__setattr__(self, __WRAPPER_KEY__, DataFeedWrapper(self))
    return getattr(self, __WRAPPER_KEY__)


setattr(pd.DataFrame, "l", _lettrade_wrapper)
