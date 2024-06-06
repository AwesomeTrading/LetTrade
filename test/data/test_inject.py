import unittest

import pandas as pd

from lettrade.data import DataFeed
from lettrade.exchange.backtest.data import CSVBackTestDataFeed


class DataFeedInjectTestCase(unittest.TestCase):
    def setUp(self):
        self.data: DataFeed = CSVBackTestDataFeed("test/assets/EURUSD_1h-0_1000.csv")
        self.data._set_main()

    def test_pointer(self):
        df = self.data.copy(deep=True)

        self.assertEqual(df.l[0].name, df.l.index[0], "Data[0] index value wrong")
        self.assertEqual(df.l[0].open, df.l.open[0], "Data[0] open value wrong")
        self.assertEqual(df.l[0].high, df.l.high[0], "Data[0] high value wrong")
        self.assertEqual(df.l[0].low, df.l.low[0], "Data[0] low value wrong")
        self.assertEqual(df.l[0].close, df.l.close[0], "Data[0] close value wrong")
        self.assertEqual(df.l[0].volume, df.l.volume[0], "Data[0] volume value wrong")

        self.assertIs(
            df.l._pointer,
            df.l.index.pointer,
            "Data.l._pointer value wrong",
        )
        self.assertIs(
            df.l._pointer,
            df.l.open.pointer,
            "Data.l._pointer value wrong",
        )
        self.assertIs(
            df.l._pointer,
            df.l.high.pointer,
            "Data.l._pointer value wrong",
        )
        self.assertIs(
            df.l._pointer,
            df.l.low.pointer,
            "Data.l._pointer value wrong",
        )
        self.assertIs(
            df.l._pointer,
            df.l.close.pointer,
            "Data.l._pointer value wrong",
        )
        self.assertIs(
            df.l._pointer,
            df.l.volume.pointer,
            "Data.l._pointer value wrong",
        )

    def test_next(self):
        df = self.data.copy(deep=True)

        df.next()
        self.assertEqual(
            df.l.pointer,
            df.l.index.pointer,
            "Data.l.pointer value wrong",
        )
        self.assertEqual(
            df.open.iloc[1],
            df.l.open.iloc[0],
            "Data..l.open.iloc[0] value wrong",
        )

    def test_overrite_index(self):
        df = self.data.copy(deep=True)

        index_id = id(df.index)
        pointer_id = id(df.l.pointer)

        dt = pd.Timestamp("2024-01-01 00:00:00")

        self.assertTrue(df[df.index == dt].empty, f"Datetime {dt} existed in data")

        df.loc[dt, ["open", "close"]] = [1, 2]

        self.assertNotEqual(index_id, id(df.index))
        self.assertEqual(pointer_id, id(df.l.index.pointer))

    def test_set_index(self):
        df = self.data.copy(deep=True)

        index_id = id(df.index)
        pointer_id = id(df.l.pointer)

        df.reset_index(inplace=True)
        df.set_index("datetime", inplace=True)

        self.assertNotEqual(index_id, id(df.index))
        self.assertEqual(pointer_id, id(df.l.index.pointer))


if __name__ == "__main__":
    unittest.main(verbosity=2)
