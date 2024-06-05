import unittest

import pandas as pd
from pandas import testing as pdtest

from lettrade.exchange.backtest.data import CSVBackTestDataFeed


class DataFeedInjectTestCase(unittest.TestCase):
    def setUp(self):
        self.data = CSVBackTestDataFeed("test/assets/EURUSD_1h-0_1000.csv")
        self.data._set_main()

    def test_pointer(self):
        df = self.data.copy(deep=True)

        self.assertEqual(df.l[0].name, df.index.l[0], "Data[0] index value wrong")
        self.assertEqual(df.l[0].open, df.open.l[0], "Data[0] open value wrong")
        self.assertEqual(df.l[0].high, df.high.l[0], "Data[0] high value wrong")
        self.assertEqual(df.l[0].low, df.low.l[0], "Data[0] low value wrong")
        self.assertEqual(df.l[0].close, df.close.l[0], "Data[0] close value wrong")
        self.assertEqual(df.l[0].volume, df.volume.l[0], "Data[0] volume value wrong")

        self.assertIs(
            df.l._pointers,
            df.index.l._pointers,
            "Data.l._pointers value wrong",
        )
        self.assertIs(
            df.l._pointers,
            df.open.l._pointers,
            "Data.l._pointers value wrong",
        )
        self.assertIs(
            df.l._pointers,
            df.high.l._pointers,
            "Data.l._pointers value wrong",
        )
        self.assertIs(
            df.l._pointers,
            df.low.l._pointers,
            "Data.l._pointers value wrong",
        )
        self.assertIs(
            df.l._pointers,
            df.close.l._pointers,
            "Data.l._pointers value wrong",
        )
        self.assertIs(
            df.l._pointers,
            df.volume.l._pointers,
            "Data.l._pointers value wrong",
        )

    def test_next(self):
        df = self.data.copy(deep=True)

        df.next()
        self.assertEqual(
            df.l.pointer,
            df.index.l.pointer,
            "Data.l.pointer value wrong",
        )
        self.assertEqual(
            df.l.pointer,
            df.open.l.pointer,
            "Data.l.pointer value wrong",
        )

    def test_index_overrite(self):
        df = self.data.copy(deep=True)

        index_id = id(df.index)
        pointer_id = id(df.l._pointers)

        dt = pd.Timestamp("2024-01-01 00:00:00")

        self.assertTrue(df[df.index == dt].empty, f"Datetime {dt} existed in data")

        df.loc[dt, ["open", "close"]] = [1, 2]

        self.assertNotEqual(index_id, id(df.index))
        self.assertEqual(pointer_id, id(df.index.l._pointers))


if __name__ == "__main__":
    unittest.main(verbosity=2)
