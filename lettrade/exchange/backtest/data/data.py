import pandas as pd

from lettrade.data import CSVDataFeed, DataFeed


class BackTestDataFeed(DataFeed):
    def alive(self):
        return self.index[-1] > 0

    def next(self) -> bool:
        self.index -= 1
        return True


class CSVBackTestDataFeed(CSVDataFeed, BackTestDataFeed):
    pass
