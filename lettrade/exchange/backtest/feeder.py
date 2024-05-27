import numpy as np

from lettrade.base.error import LetTradeNoMoreData
from lettrade.data import DataFeeder

from .data import BackTestDataFeed


class BackTestDataFeeder(DataFeeder):
    """BackTest DataFeeder"""

    datas: list[BackTestDataFeed]
    data: BackTestDataFeed

    @property
    def is_continous(self):
        """Flag check is realtime continous datafeeder"""
        return False

    def alive(self):
        return self.data.alive()

    def next(self):
        # End of main data
        if self.data.index.stop <= 0:
            return False

        next = self.data.datetime[1]

        has_next = True
        for data in self.datas:
            if not data.next(next=next):
                has_next = False

        if not has_next:
            raise LetTradeNoMoreData()

    def start(self, size=100):
        next = self.data.datetime[size]
        for data in self.datas:
            data.next(size=size, next=next)
