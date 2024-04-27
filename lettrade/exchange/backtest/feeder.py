import numpy as np

from lettrade.data import DataFeeder

from .data import BackTestDataFeed


class BackTestDataFeeder(DataFeeder):
    datas: list[BackTestDataFeed]
    data: BackTestDataFeed

    def alive(self):
        return self.data.alive()

    def next(self):
        return self.data.next()

    def pre_feed(self, size=100):
        self.data.next(size)
