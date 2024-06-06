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
        # print("-----> ILocWrapper", data.name, type(data))

    # def __getattr__(self, name: str):
    #     if hasattr(self._data.iloc, name):
    #         return getattr(self._data.iloc, name)
    #     raise NotImplementedError(f"Method {name} is not implement yet")

    def __getitem__(self, item: int | slice):
        if isinstance(item, int):
            item += self._owner._pointer
        elif isinstance(item, slice):
            item = slice(
                item.start + self._owner._pointer,
                item.stop + self._owner._pointer,
                item.step,
            )
        else:
            raise NotImplementedError(
                f"Get item {item} type {type(item)} is not implement yet"
            )

        return self._data._values[item]

    # Property
    @property
    def pointer(self):
        return self._owner._pointer


class IndexWapper:
    _data: pd.DatetimeIndex
    _owner: "DataFeedWrapper"

    def __init__(self, data, owner) -> None:
        self._data = data
        self._owner = owner
        # print("-----> IndexWapper", data.name, type(data))

    def __getattr__(self, name: str):
        return getattr(self._data, name)
        # if hasattr(self._data, name):
        #     return getattr(self._data, name)
        # raise NotImplementedError(f"Method {name} is not implement yet")

    def __getitem__(self, item: int | slice):
        if isinstance(item, int):
            item += self._owner._pointer
        elif isinstance(item, slice):
            item = slice(
                item.start + self._owner._pointer,
                item.stop + self._owner._pointer,
                item.step,
            )
        else:
            raise NotImplementedError(
                f"Get item {item} type {type(item)} is not implement yet"
            )
        return self._data._values[item]

    # Property
    @property
    def pointer(self):
        return self._owner._pointer


class SeriesWapper:
    _data: pd.DatetimeIndex
    _owner: "DataFeedWrapper"
    _iloc: ILocWrapper

    def __init__(self, data, owner) -> None:
        self._data = data
        self._owner = owner
        self._iloc = ILocWrapper(self._data, self._owner)

        # print("-----> SeriesWapper", data.name, type(data))

    def __getattr__(self, name: str):
        return getattr(self._data, name)
        # if hasattr(self._data, name):
        #     return getattr(self._data, name)
        # raise NotImplementedError(f"Method {name} is not implement yet")

    def __getitem__(self, item: int | slice | Any):
        return self._iloc[item]
        # if isinstance(item, (int, slice)):
        #     return self._iloc[item]
        # return self._data[item]

    # Property
    @property
    def iloc(self) -> _iLocIndexer:
        return self._iloc

    @property
    def pointer(self):
        return self._owner._pointer


class DataFeedWrapper:
    _data: pd.DataFrame
    _pointer: int
    _iloc: ILocWrapper

    def __init__(self, data: pd.DataFrame) -> None:
        # Validate new instance not load an existed wrapper
        if hasattr(data.index, __WRAPPER_KEY__):
            raise RuntimeError("DataFeed.index reuses a loaded wrapper")
        for column in data.columns:
            if hasattr(data[column], __WRAPPER_KEY__):
                raise RuntimeError(f"DataFeed.{column} reuses a loaded wrapper")

        self._pointer = 0
        self._data = data
        self._iloc = ILocWrapper(self._data, self)

    def __getattr__(
        self, name: str
    ) -> pd.Series | pd.Index | pd.DatetimeIndex | SeriesWapper | IndexWapper:
        # if hasattr(self._data, name):
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

        # raise NotImplementedError(f"Method {name} is not implement yet")

    def __getitem__(self, item: int | slice | str | Any):
        # return self._iloc[item]
        if isinstance(item, (int, slice)):
            return self._iloc[item]
        return self._data[item]

    # Function
    def next(self, size=1):
        self._pointer += size

    def go_start(self) -> None:
        self._pointer = 0

    def go_stop(self) -> None:
        self._pointer = len(self._data) - 1

    def reset(self) -> None:
        self._pointer = 0

    # Property
    @property
    def iloc(self) -> _iLocIndexer:
        return self._iloc

    @property
    def pointer(self):
        return self._pointer

    @property
    def pointer_start(self):
        return -self._pointer

    @property
    def pointer_stop(self):
        return len(self._data) - self._pointer


# @property
# def _lettrade_wrapper(self) -> DataFeedWrapper:
#     if not hasattr(self, __WRAPPER_KEY__):
#         object.__setattr__(self, __WRAPPER_KEY__, DataFeedWrapper(self))
#     return getattr(self, __WRAPPER_KEY__)


# setattr(pd.DataFrame, "l", _lettrade_wrapper)
