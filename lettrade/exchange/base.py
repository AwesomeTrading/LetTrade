from datetime import datetime
from enum import Enum
from typing import Generic, TypeVar

T = TypeVar("T")


class State(Enum):
    Open = "open"
    Pending = "pending"
    Close = "close"


class OrderType(Enum):
    Market = "market"
    Limit = "limit"
    Stop = "stop"


class BaseTransaction:
    def __init__(
        self,
        id: str,
        exchange: "Exchange",
        data: "DataFeed",
        size: float,
        created_at: datetime = None,
    ) -> None:
        self.__id: str = id
        self.__exchange: "Exchange" = exchange
        self.__data: "DataFeed" = data
        self.__size: float = size

        if created_at is None:
            created_at = self.__exchange.now
        self.__created_at: datetime = created_at

    def _replace(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, f"_{self.__class__.__qualname__}__{k}", v)
        return self

    # Fields getters
    @property
    def id(self) -> str:
        return self.__id

    @property
    def data(self) -> "DataFeed":
        return self.__data

    @property
    def size(self) -> float:
        return self.__size

    @property
    def created_at(self) -> float:
        return self.__created_at

    @property
    def exchange(self) -> "Exchange":
        return self.__exchange


class FastSet(Generic[T]):
    __dict: dict[str, T]
    __id_index: list[str]

    __type_t: T = None

    def __init__(self) -> None:
        self.__dict = {}
        self.__id_index = []

    def __getitem__(self, name: int | str):
        if isinstance(name, int):
            name = self.__id_index[name]
        return self.__dict[name]

    def __setitem__(self, name: int | str, value: T):
        if isinstance(name, int):
            name = self.__id_index[name]

        self.__dict[value] = value

    def __len__(self):
        return len(self.__id_index)

    def __delitem__(self, name: int | str):
        if isinstance(name, int):
            i = name
            name = self.__id_index[i]
            del self.__id_index[i]

        del self.__dict[name]

    def add(self, *datas: list[T]):
        for data in datas:
            if not self.isinstance(data):
                raise RuntimeError(f"Data {data} is not type {T}")

            if data.id in self.__id_index:
                raise RuntimeError(f"Data id {data.id} existed")

            self.__dict[data.id] = data
            self.__id_index.append(data.id)

    def set(self, *datas: list[T]):
        for data in datas:
            if not self.isinstance(data):
                raise RuntimeError(f"Data {data} is not type {T}")

            self.__dict[data.id] = data
            self.__id_index.append(data.id)

    def remove(self, name: int | str | T):
        i = None
        if isinstance(name, int):
            i = name
            name = self.__id_index[i]
        if self.isinstance(name):
            obj = name
            name = obj.id
        if isinstance(name, str) and i is None:
            i = self.__id_index.index(name)

        del self.__id_index[i]
        del self.__dict[name]

    def isinstance(self, obj):
        if self.__type_t is None:
            self.__type_t = self.__orig_class__.__args__[0]
        return isinstance(obj, self.__type_t)
