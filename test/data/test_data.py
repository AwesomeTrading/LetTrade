import unittest

import pandas as pd
from pandas import testing as pdtest

from lettrade.exchange.backtest.data import CSVBackTestDataFeed


class DataFeedTestCase(unittest.TestCase):
    def setUp(self):
        self.data = CSVBackTestDataFeed("test/assets/EURUSD_1h-0_1000.csv")
        self.raw_data = pd.read_csv(
            "test/assets/EURUSD_1h-0_1000.csv",
            index_col=0,
            parse_dates=["datetime"],
        )

    def test_value(self):
        pdtest.assert_frame_equal(
            self.data,
            self.raw_data,
            "DataFrame is not equal pandas.DataFrame",
            check_index_type=False,
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
