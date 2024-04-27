from abc import ABCMeta, abstractmethod
from typing import Optional

from lettrade.base import BaseDataFeeds
from lettrade.data import DataFeed, DataFeeder


class Exchange(BaseDataFeeds, metaclass=ABCMeta):

    def __init__(self):
        self.feeder: DataFeeder = None

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
