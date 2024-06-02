import pandas as pd


class IndexInject:
    _pointers: list[int]
    _owner: pd.DataFrame | pd.Series | pd.DatetimeIndex

    def __init__(self, owner) -> None:
        index = owner.index if hasattr(owner, "index") else owner
        if not isinstance(index, pd.DatetimeIndex):
            raise RuntimeError("Index is not instance of pd.DatetimeIndex")

        if not hasattr(index, "_lt_pointers"):
            setattr(index, "_lt_pointers", [0])
        self._pointers = getattr(index, "_lt_pointers")

        self._owner = owner

    def __getitem__(self, value):
        return self._owner._values[value + self.pointer]

    # Function
    def next(self, next=0):
        self._pointers[0] += next

    # Pointer
    @property
    def pointer(self):
        return self._pointers[0]

    def go_start(self):
        self._pointers[0] = 0

    def go_stop(self):
        self._pointers[0] = len(self._owner) - 1

    def reset(self, *args, **kwargs):
        self._pointers[0] = 0

    @property
    def start(self) -> int:
        return -self._pointers[0]

    @property
    def stop(self) -> int:
        return len(self._owner) - self._pointers[0]


class SeriesInject(IndexInject):
    pass


class DataFrameInject(IndexInject):
    def __getitem__(self, value):
        return self._owner.iloc[value + self.pointer]


@property
def _lettrade_injector(self):
    if not hasattr(self, "_lt_inject"):
        if isinstance(self, pd.DataFrame):
            inject = DataFrameInject(self)
        elif isinstance(self, pd.Series):
            inject = SeriesInject(self)
        if isinstance(self, pd.DatetimeIndex):
            inject = IndexInject(self)

        setattr(self, "_lt_inject", inject)

    return self._lt_inject


setattr(pd.DataFrame, "l", _lettrade_injector)
setattr(pd.Series, "l", _lettrade_injector)
setattr(pd.DatetimeIndex, "l", _lettrade_injector)
