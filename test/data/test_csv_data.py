import unittest

import pandas as pd

from lettrade.data import DataFeed, DataFeedIndex, TimeFrame
from lettrade.exchange.backtest.data import CSVBackTestDataFeed


class CSVBackTestDataFeedTestCase(unittest.TestCase):
    def setUp(self):
        self.data = CSVBackTestDataFeed("test/assets/EURUSD_1h-0_1000.csv")

    def test_types(self):
        self.assertIsInstance(
            self.data,
            DataFeed,
            "Data is not instance of DataFeed",
        )

        self.assertIsInstance(
            self.data.index,
            pd.DatetimeIndex,
            "Index is not instance of pd.DatetimeIndex",
        )

        self.assertIsInstance(
            self.data.index,
            DataFeedIndex,
            "Index is not instance of DataFeedIndex",
        )

        self.assertIsInstance(
            self.data.timeframe,
            TimeFrame,
            "timeframe is not instance of TimeFrame",
        )

    def test_name(self):
        self.assertEqual(self.data.name, "EURUSD_1h", "Name is wrong")

    def test_size(self):
        self.assertEqual(len(self.data), 1_000, "Size is wrong")

    def test_copy(self):
        df = self.data.copy(deep=True)
        # Test copy types
        self.assertIsInstance(
            df,
            self.data.__class__,
            f"Copy data is not instance of {self.data.__class__}",
        )
        self.assertIsInstance(
            df.index,
            self.data.index.__class__,
            f"Copy data.index is not instance of {self.data.index.__class__}",
        )
        self.assertIsInstance(
            df.index,
            self.data.timeframe.__class__,
            f"Copy data.timeframe is not instance of {self.data.timeframe.__class__}",
        )

        # Test deepcopy is not a mirror
        df.loc[0, "open"] = 0
        self.assertEqual(df.loc[0, "open"], 0, "Set value to data.open error")
        self.assertNotEqual(self.data.loc[0, "open"], 0, "Value change when deepcopy")

        # Test set value
        df[0].open = 1
        self.assertEqual(df.loc[0, "open"], 1, "Set value to data.open error")

    # Test drop
    def test_drop(self):
        df = self.data.copy(deep=True)
        df.drop_since(100)

        self.assertEqual(len(df), 900, "Drop data size wrong")
        self.assertEqual(df.open[0], 0.99474, "Drop data open value wrong")
        self.assertEqual(len(self.data), 1_000, "self.data size wrong")
        self.assertEqual(self.data.open[0], 0.97724, "self.data open value wrong")
