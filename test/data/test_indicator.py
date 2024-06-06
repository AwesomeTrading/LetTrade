import unittest

import numpy as np
import pandas as pd
import pandas_ta as pdta
import talib.abstract as ta
from pandas import testing as pdtest

from lettrade.exchange.backtest.data import CSVBackTestDataFeed


class IndicatorTestCase(unittest.TestCase):
    def setUp(self):
        self.data = CSVBackTestDataFeed("test/assets/EURUSD_1h-0_1000.csv")
        self.data._set_main()

        self.raw_data = pd.read_csv(
            "test/assets/EURUSD_1h-0_1000.csv",
            index_col=0,
            parse_dates=["datetime"],
        )

        # Ta-Lib
        self.ta_ema = ta.EMA(self.data, timeperiod=21)
        self.ta_ema_raw = ta.EMA(self.raw_data, timeperiod=21)

        # Pandas_TA
        self.pdta_ema = pdta.ema(self.data.close, length=21)
        self.pdta_ema_raw = pdta.ema(self.raw_data.close, length=21)

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

    def test_indicator(self):
        pdtest.assert_series_equal(
            self.ta_ema,
            self.pdta_ema,
            check_names=False,
        )
        pdtest.assert_series_equal(
            self.ta_ema,
            self.ta_ema_raw,
            check_names=False,
            check_index_type=False,
        )
        pdtest.assert_series_equal(
            self.pdta_ema,
            self.pdta_ema_raw,
            check_names=False,
            check_index_type=False,
        )
        pdtest.assert_series_equal(
            self.ta_ema_raw,
            self.pdta_ema_raw,
            check_names=False,
        )

    def test_next(self):
        df = self.data.copy(deep=True)
        df["ema"] = self.ta_ema

        for i in range(0, len(df)):
            ema_value = df.l.ema[0]
            raw_ema_value = self.ta_ema_raw.iloc[i]

            # Next first to by pass next continue condiction
            df.next()

            if np.isnan(ema_value) and np.isnan(raw_ema_value):
                continue

            self.assertEqual(ema_value, raw_ema_value, f"EMA[{i}] is wrong")


if __name__ == "__main__":
    unittest.main(verbosity=2)
