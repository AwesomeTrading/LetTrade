import unittest

import numpy as np
import pandas as pd

# import talib.abstract as ta
from pandas import testing as pdtest

from lettrade.exchange.backtest.data import CSVBackTestDataFeed
from lettrade.indicator.vendor import qtpylib as ql


class FastFinanceIndicatorTestCase(unittest.TestCase):
    def setUp(self):
        self.data = CSVBackTestDataFeed("test/assets/EURUSD_1h-0_1000.csv")
        self.data._set_main()

        self.raw_data = pd.read_csv(
            "test/assets/EURUSD_1h-0_1000.csv",
            index_col=0,
            parse_dates=["datetime"],
        )

        # QTPyLib
        self.ql_ema = ql.ema(self.data.close, window=21)
        self.ql_ema_raw = ql.ema(self.raw_data.close, window=21)

    def test_types(self):
        self.assertIsInstance(
            self.ql_ema,
            pd.Series,
            "QTPyLib EMA is not instance of pandas.Series",
        )

    # def test_indicator(self):
    #     pdtest.assert_series_equal(
    #         self.ql_ema,
    #         self.ff_ema,
    #         check_names=False,
    #         check_dtype=False,
    #     )
    #     pdtest.assert_series_equal(
    #         self.ql_ema,
    #         self.ql_ema_raw,
    #         check_names=False,
    #         # check_index_type=False,
    #     )
    #     pdtest.assert_series_equal(
    #         self.ff_ema,
    #         self.ff_ema_raw,
    #         check_names=False,
    #         # check_index_type=False,
    #     )
    #     pdtest.assert_series_equal(
    #         self.ql_ema_raw,
    #         self.ff_ema_raw,
    #         check_names=False,
    #     )

    def test_next(self):
        df = self.data.copy(deep=True)
        df["ema"] = self.ql_ema

        for i in range(0, len(df)):
            ema_value = df.l.ema[0]
            raw_ema_value = self.ql_ema_raw.iloc[i]

            # Next first to by pass next continue condiction
            df.next()

            if np.isnan(ema_value) and np.isnan(raw_ema_value):
                continue

            self.assertEqual(ema_value, raw_ema_value, f"EMA[{i}] is wrong")


if __name__ == "__main__":
    unittest.main(verbosity=2)
