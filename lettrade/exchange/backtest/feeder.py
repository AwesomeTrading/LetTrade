import numpy as np

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
        for data in self.datas:
            data.next()

    def start(self, size=100):
        for data in self.datas:
            data.next(size)
