from abc import ABCMeta, abstractmethod

from .data import DataFeed


class DataFeeder(metaclass=ABCMeta):
    data: DataFeed
    datas: list[DataFeed]

    def __init__(self, datas: list[DataFeed]) -> None:
        self.datas = datas
        self.data = datas[0]

    @abstractmethod
    def alive(self):
        pass

    @abstractmethod
    def pre_feed(self):
        pass

    @abstractmethod
    def next(self):
        pass
