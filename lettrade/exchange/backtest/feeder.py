import numpy as np

from lettrade.data import DataFeeder

from .data import BackTestDataFeed


class BackTestDataFeeder(DataFeeder):
    datas: list[BackTestDataFeed]
    data: BackTestDataFeed

    @property
    def is_continous(self):
        """Flag check is realtime continous datafeeder"""
        return False

    def alive(self):
        return self.data.alive()

    def next(self):
        return self.data.next()

    def start(self, size=100):
        self.data.next(size)
