import unittest

import pandas as pd
import pandas_ta as pdta
import talib.abstract as ta
from pandas import testing as pdtest

from lettrade.exchange.backtest.data import CSVBackTestDataFeed


class IndicatorTestCase(unittest.TestCase):
    def setUp(self):
        self.data = CSVBackTestDataFeed("test/assets/EURUSD_1h-0_1000.csv")

        # Ta-Lib
        self.ta_ema = ta.EMA(self.data, timeperiod=21)

        # Pandas_TA
        self.pdta_ema = pdta.ema(self.data.close, length=21)
        self.pdta_ema.name = None

    def test_types(self):
        self.assertIsInstance(
            self.ta_ema,
            pd.Series,
            "TaLib EMA is not instance of pandas.Series",
        )
        self.assertIsInstance(
            self.pdta_ema,
            pd.Series,
            "Pandas_ta EMA is not instance of pandas.Series",
        )

    def test_value(self):
        pdtest.assert_series_equal(self.ta_ema, self.pdta_ema)


if __name__ == "__main__":
    unittest.main(verbosity=2)
