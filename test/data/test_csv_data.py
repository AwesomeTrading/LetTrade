import unittest

import pandas as pd

from lettrade.data import DataFeed, TimeFrame
from lettrade.exchange.backtest.data import CSVBackTestDataFeed


class CSVBackTestDataFeedTestCase(unittest.TestCase):
    def setUp(self):
        self.data = CSVBackTestDataFeed("test/assets/EURUSD_1h-0_1000.csv")
        self.data._set_main()

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

        # self.assertIsInstance(
        #     self.data.index,
        #     DataFeedIndex,
        #     "Index is not instance of DataFeedIndex",
        # )

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
            df.timeframe,
            self.data.timeframe.__class__,
            f"Copy data.timeframe is not instance of {self.data.timeframe.__class__}",
        )

        # Test deepcopy is not a mirror
        loc = df.l.index[0]
        df.loc[loc, "open"] = 0
        self.assertEqual(df.loc[loc, "open"], 0, "Set value to data.open error")
        self.assertEqual(df.l[0].open, 0, "Set value to data.open error")
        self.assertNotEqual(self.data.loc[loc, "open"], 0, "Value change when deepcopy")

        loc = df.l.index[1]
        df.at[loc, "close"] = 1
        self.assertEqual(df.loc[loc, "close"], 1, "Set value to data.open error")
        self.assertEqual(df.l[1].close, 1, "Set value to data.open error")
        self.assertNotEqual(
            self.data.loc[loc, "close"], 1, "Value change when deepcopy"
        )

    # Test drop
    def test_drop(self):
        df: DataFeed = self.data.copy(deep=True)
        df.drop(since=100)

        self.assertEqual(len(df), 900, "Drop data size wrong")
        self.assertEqual(df.l.open[0], 0.99474, "Drop data open value wrong")
        self.assertEqual(len(self.data), 1_000, "self.data size wrong")
        self.assertEqual(self.data.l.open[0], 0.97724, "self.data open value wrong")

    # Test index
    def test_index(self):
        df = self.data.copy(deep=True)

        # Move to nexts rows
        next = 3
        df.next(next)
        self.assertEqual(df.l.pointer, next, "Data pointer wrong")

        self.assertEqual(df.l.open[0], 0.97656, f"Data.open[{next}] wrong")
        self.assertEqual(df.l.high[0], 0.97718, f"Data.high[{next}] wrong")
        self.assertEqual(df.l.low[0], 0.97585, f"Data.low[{next}] wrong")
        self.assertEqual(df.l.close[0], 0.9765, f"Data.close[{next}] wrong")
        self.assertEqual(df.l.volume[0], 5050.0, f"Data.volume[{next}] wrong")
        self.assertEqual(
            df.l.index[0],
            pd.Timestamp("2022-10-20 03:00:00"),
            f"Data.index[{next}] wrong",
        )

        # Move to end
        end = len(df) - 1
        df.l.go_stop()
        self.assertEqual(df.l.pointer, end, "Data pointer wrong")
        self.assertEqual(df.l.open[0], 1.06215, f"Data.open[{end}] wrong")
        self.assertEqual(df.l.high[0], 1.06359, f"Data.high[{end}] wrong")
        self.assertEqual(df.l.low[0], 1.06134, f"Data.low[{end}] wrong")
        self.assertEqual(df.l.close[0], 1.06341, f"Data.close[{end}] wrong")
        self.assertEqual(df.l.volume[0], 5679.0, f"Data.volume[{end}] wrong")
        self.assertEqual(
            df.l.index[0],
            pd.Timestamp("2022-12-16 15:00:00"),
            f"Data.index[{end}] wrong",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
