from abc import ABCMeta, abstractmethod
from typing import Optional

from lettrade.data import DataFeed, DataFeeder


class Exchange(metaclass=ABCMeta):
    feeder: DataFeeder
    datas: list[DataFeed] = None
    data: DataFeed

    # def __init__(self) -> None:
    #     pass

    def _load(self, feeder):
        if self.datas:
            print("[WARN] Reloading datas...")

        self.feeder = feeder
        self.datas = feeder.datas
        self.data = feeder.datas[0]

    @abstractmethod
    def new_order(
        self,
        size: float,
        limit: Optional[float] = None,
        stop: Optional[float] = None,
        sl: Optional[float] = None,
        tp: Optional[float] = None,
        tag: object = None,
        *args,
        **kwargs
    ):
        raise NotImplementedError("Exchange.new_order not implement yet")
