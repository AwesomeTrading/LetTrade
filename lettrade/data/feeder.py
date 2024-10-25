from abc import ABCMeta, abstractmethod

from .data import DataFeed


class DataFeeder(metaclass=ABCMeta):
    datas: list[DataFeed]
    data: DataFeed

    def init(self, datas: list[DataFeed]):
        self.datas = datas
        self.data = datas[0]

    @property
    def is_continous(self):
        """Flag check is realtime continous datafeeder"""
        return True

    def alive(self):
        pass

    def start(self, **kwargs):
        """Load init datafeeds"""

    @abstractmethod
    def next(self):
        pass

    def stop(self):
        pass
