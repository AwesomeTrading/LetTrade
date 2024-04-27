import pandas as pd

from lettrade.data import CSVDataFeed, DataFeed


class BackTestDataFeed(DataFeed):
    def alive(self):
        return self.index[-1] > 0

    def next(self, size=1) -> bool:
        self.index -= size
        return True


class CSVBackTestDataFeed(CSVDataFeed, BackTestDataFeed):
    pass
