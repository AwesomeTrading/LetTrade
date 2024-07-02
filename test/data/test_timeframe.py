import unittest

import pandas as pd

from lettrade.data import TimeFrame


class DataFeedInjectTestCase(unittest.TestCase):
    def test_int(self):
        tf = TimeFrame(1)
        self.assertEqual(tf.string, "1m")

    def test_string(self):
        tf = TimeFrame("3s")
        self.assertEqual(tf.string, "3s")

        tf = TimeFrame("5m")
        self.assertEqual(tf.string, "5m")

        tf = TimeFrame("2h")
        self.assertEqual(tf.string, "2h")

        tf = TimeFrame("12h")
        self.assertEqual(tf.string, "12h")

        tf = TimeFrame("1d")
        self.assertEqual(tf.string, "1d")

        tf = TimeFrame("3d")
        self.assertEqual(tf.string, "3d")

    def test_timedelta(self):
        tf = TimeFrame(pd.Timedelta(minutes=3))
        self.assertEqual(tf.string, "3m")

        tf = TimeFrame(pd.Timedelta(hours=3))
        self.assertEqual(tf.string, "3h")

        tf = TimeFrame(pd.Timedelta(days=1))
        self.assertEqual(tf.string, "1d")

        tf = TimeFrame(pd.Timedelta(weeks=1))
        self.assertEqual(tf.string, "1w")

    def test_list(self):
        tf = TimeFrame([3, "s"])
        self.assertEqual(tf.string, "3s")

        tf = TimeFrame([1, "m"])
        self.assertEqual(tf.string, "1m")

        tf = TimeFrame([7, "h"])
        self.assertEqual(tf.string, "7h")

        tf = TimeFrame([1, "w"])
        self.assertEqual(tf.string, "1w")

    def test_exception(self):
        with self.assertRaises(RuntimeError):
            TimeFrame("asd123")

        with self.assertRaises(RuntimeError):
            TimeFrame("1a")

        with self.assertRaises(RuntimeError):
            TimeFrame("1z")

        with self.assertRaises(RuntimeError):
            TimeFrame(pd.Timestamp("2020-01-01"))

        with self.assertRaises(RuntimeError):
            TimeFrame("12d")

        with self.assertRaises(RuntimeError):
            TimeFrame("-1d")

    def test_floor(self):
        # Second
        tf = TimeFrame("5s")

        floor = tf.floor(pd.Timestamp("2020-01-01 01:00:03"))
        self.assertEqual(floor, pd.Timestamp("2020-01-01 01:00:00"))

        floor = tf.floor(pd.Timestamp("2020-01-01 01:00:23"))
        self.assertEqual(floor, pd.Timestamp("2020-01-01 01:00:20"))

        # Minute
        tf = TimeFrame("5m")

        floor = tf.floor(pd.Timestamp("2020-01-01 01:00:03"))
        self.assertEqual(floor, pd.Timestamp("2020-01-01 01:00:00"))

        floor = tf.floor(pd.Timestamp("2020-01-01 01:12:23"))
        self.assertEqual(floor, pd.Timestamp("2020-01-01 01:10:00"))

        # Hour
        tf = TimeFrame("4h")

        floor = tf.floor(pd.Timestamp("2020-01-01 11:11:03"))
        self.assertEqual(floor, pd.Timestamp("2020-01-01 8:00:00"))

        floor = tf.floor(pd.Timestamp("2020-01-01 21:12:23"))
        self.assertEqual(floor, pd.Timestamp("2020-01-01 20:00:00"))

        # Hour
        tf = TimeFrame("3h")

        floor = tf.floor(pd.Timestamp("2020-01-01 02:11:03"))
        self.assertEqual(floor, pd.Timestamp("2020-01-01 00:00:00"))

        floor = tf.floor(pd.Timestamp("2020-01-01 21:12:23"))
        self.assertEqual(floor, pd.Timestamp("2020-01-01 21:00:00"))

        # # Hour
        # tf = TimeFrame("7h")

        # floor = tf.floor(pd.Timestamp("2020-01-01 02:11:03"))
        # self.assertEqual(floor, pd.Timestamp("2020-01-01 00:00:00"))

        # floor = tf.floor(pd.Timestamp("2020-01-01 15:12:23"))
        # self.assertEqual(floor, pd.Timestamp("2020-01-01 14:00:00"))

        # Week
        tf = TimeFrame("1w")

        floor = tf.floor(pd.Timestamp("2020-01-01 11:11:03"))
        self.assertEqual(floor, pd.Timestamp("2019-12-30 00:00:00"))

        floor = tf.floor(pd.Timestamp("2020-03-03 21:12:23"))
        self.assertEqual(floor, pd.Timestamp("2020-03-02 00:00:00"))

    def test_ceil(self):
        # Second
        tf = TimeFrame("5s")

        ceil = tf.ceil(pd.Timestamp("2020-01-01 01:00:03"))
        self.assertEqual(ceil, pd.Timestamp("2020-01-01 01:00:05"))

        ceil = tf.ceil(pd.Timestamp("2020-01-01 01:00:23"))
        self.assertEqual(ceil, pd.Timestamp("2020-01-01 01:00:25"))

        # Minute
        tf = TimeFrame("5m")

        ceil = tf.ceil(pd.Timestamp("2020-01-01 01:00:03"))
        self.assertEqual(ceil, pd.Timestamp("2020-01-01 01:05:00"))

        ceil = tf.ceil(pd.Timestamp("2020-01-01 01:12:23"))
        self.assertEqual(ceil, pd.Timestamp("2020-01-01 01:15:00"))

        # Hour
        tf = TimeFrame("4h")

        ceil = tf.ceil(pd.Timestamp("2020-01-01 11:11:03"))
        self.assertEqual(ceil, pd.Timestamp("2020-01-01 12:00:00"))

        ceil = tf.ceil(pd.Timestamp("2020-01-01 21:12:23"))
        self.assertEqual(ceil, pd.Timestamp("2020-01-02 00:00:00"))

        # Day
        tf = TimeFrame("1d")

        ceil = tf.ceil(pd.Timestamp("2020-01-01 11:11:03"))
        self.assertEqual(ceil, pd.Timestamp("2020-01-02 00:00:00"))

        ceil = tf.ceil(pd.Timestamp("2020-03-03 21:12:23"))
        self.assertEqual(ceil, pd.Timestamp("2020-03-04 00:00:00"))

        # Week
        tf = TimeFrame("1w")

        ceil = tf.ceil(pd.Timestamp("2020-01-01 11:11:03"))
        self.assertEqual(ceil, pd.Timestamp("2020-01-06 00:00:00"))

        ceil = tf.ceil(pd.Timestamp("2020-03-03 21:12:23"))
        self.assertEqual(ceil, pd.Timestamp("2020-03-09 00:00:00"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
