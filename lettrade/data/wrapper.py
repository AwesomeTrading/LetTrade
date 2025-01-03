from typing import Any

import pandas as pd
from pandas.core.indexing import _iLocIndexer


class LetILocWrapper:
    """Wrap iloc object from DataFeed"""

    _data: pd.DatetimeIndex
    _owner: "LetDataFeedWrapper"

    def __init__(self, data, owner) -> None:
        """_summary_

        Args:
            data (_type_): DataFeed or pd.Series
            owner (_type_): DataFeed object
        """
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


class LetIndexWapper:
    """Wrap DataFeed.index"""

    _data: pd.DatetimeIndex
    _owner: "LetDataFeedWrapper"

    def __init__(self, data, owner) -> None:
        """_summary_

        Args:
            data (_type_): pandas.DatetimeIndex
            owner (_type_): DataFeed object
        """
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

    def get_loc(self, dt: pd.Timestamp) -> int:
        loc = self._data.get_loc(dt)
        return loc - self._owner._pointer

    def set_data(self, data: pd.DatetimeIndex):
        self._data = data

    # Property
    @property
    def pointer(self):
        return self._owner._pointer


class LetSeriesWapper:
    """Wrap DataFeed column"""

    _data: pd.DatetimeIndex
    _owner: "LetDataFeedWrapper"
    _iloc: LetILocWrapper | _iLocIndexer

    def __init__(self, data, owner) -> None:
        self._data = data
        self._owner = owner
        self._iloc = LetILocWrapper(self._data, self._owner)

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
    def iloc(self) -> LetILocWrapper | _iLocIndexer:
        return self._iloc

    @property
    def pointer(self):
        return self._owner._pointer

    def set_data(self, data: pd.DatetimeIndex):
        self._data = data
        self._iloc._data = data


# @pd.api.extensions.register_dataframe_accessor("l")
class LetDataFeedWrapper:
    """Wrap DataFeed"""

    _data: pd.DataFrame
    _pointer: int
    _iloc: LetILocWrapper | _iLocIndexer
    _wrappers: dict[str, LetIndexWapper | LetSeriesWapper]

    def __init__(self, data: pd.DataFrame) -> None:
        """_summary_

        Args:
            data (pd.DataFrame): DataFeed object

        Raises:
            RuntimeError: _description_
        """
        self._pointer = 0
        self._data = data
        self._iloc = LetILocWrapper(self._data, self)
        self._wrappers = dict()

    def __getattr__(
        self, name: str
    ) -> pd.Series | pd.Index | pd.DatetimeIndex | LetSeriesWapper | LetIndexWapper:
        # if hasattr(self._data, name):
        attr = getattr(self._data, name)

        # Exist
        if name in self._wrappers:
            wrapper = self._wrappers[name]
            if wrapper._data is not attr:
                wrapper.set_data(attr)
            return wrapper

        # Set wrapper
        if isinstance(attr, pd.Series):
            wrapper = LetSeriesWapper(attr, self)
            self._wrappers[name] = wrapper
            return wrapper

        if isinstance(attr, pd.DatetimeIndex):
            wrapper = LetIndexWapper(attr, self)
            self._wrappers[name] = wrapper
            return wrapper

        return attr

        # raise NotImplementedError(f"Method {name} is not implement yet")

    def __getitem__(self, item: int | slice | str | Any) -> pd.DataFrame:
        # return self._iloc[item]
        # if isinstance(item, (int, slice)):
        #     return self._iloc[item]
        if isinstance(item, int):
            return self._data.iloc[item + self._pointer]
        elif isinstance(item, slice):
            item = slice(
                item.start + self._pointer,
                item.stop + self._pointer,
                item.step,
            )
            return self._data.iloc[item]
        if isinstance(item, str):
            return self.__getattr__(item)
        return self._data[item]

    # Function
    def next(self, size=1):
        """Move pointer to next"""
        self._pointer += size

    def go_start(self) -> None:
        """Move pointer to begin"""
        self._pointer = 0

    def go_stop(self) -> None:
        """Move pointer to end"""
        self._pointer = len(self._data) - 1

    def reset(self) -> None:
        """Reset pointer to begin"""
        self._pointer = 0

    # Property
    @property
    def iloc(self) -> LetILocWrapper | _iLocIndexer:
        """Get iloc wrapper of DataFeed"""
        return self._iloc

    @property
    def pointer(self):
        """Get current pointer value"""
        return self._pointer

    @property
    def pointer_start(self):
        """Get start pointer value"""
        return -self._pointer

    @property
    def pointer_stop(self):
        """Get stop pointer value"""
        return len(self._data) - self._pointer
