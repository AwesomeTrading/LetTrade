from typing import Generic, TypeVar

T = TypeVar("T")


class FastQuery(Generic[T]):
    __dict: dict[str, T]
    __list: list[str]

    __type_t: T = None

    def __init__(self) -> None:
        self.__dict = {}
        self.__list = []

    def __getitem__(self, name: int | str):
        if isinstance(name, int):
            name = self.__list[name]
        return self.__dict[name]

    def __setitem__(self, name: int | str, value: T):
        if isinstance(name, int):
            name = self.__list[name]

        self.__dict[value] = value

    def __len__(self):
        return len(self.__list)

    def __delitem__(self, name: int | str):
        if isinstance(name, int):
            i = name
            name = self.__list[i]
            del self.__list[i]

        del self.__dict[name]

    def add(self, *datas: list[T]):
        for data in datas:
            if not self.isinstance(data):
                raise RuntimeError(f"Data {data} is not type {T}")

            if data.id in self.__list:
                raise RuntimeError(f"Data id {data.id} existed")

            self.__dict[data.id] = data
            self.__list.append(data.id)

    def set(self, *datas: list[T]):
        for data in datas:
            if not self.isinstance(data):
                raise RuntimeError(f"Data {data} is not type {T}")

            self.__dict[data.id] = data
            self.__list.append(data.id)

    def remove(self, name: int | str | T):
        i = None
        if isinstance(name, int):
            i = name
            name = self.__list[i]
        if self.isinstance(name):
            obj = name
            name = obj.id
        if isinstance(name, str) and i is None:
            i = self.__list.index(name)

        del self.__list[i]
        del self.__dict[name]

    def isinstance(self, obj):
        if self.__type_t is None:
            self.__type_t = self.__orig_class__.__args__[0]
        return isinstance(obj, self.__type_t)
