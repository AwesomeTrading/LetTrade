import math

import pytest

from lettrade.exchange.backtest import CSVBackTestDataFeed
from lettrade.indicator import ichimoku


@pytest.fixture
def dataframe():
    return CSVBackTestDataFeed("test/assets/EURUSD_1h-0_1000.csv")


### Test
def test_tenkan_sen(dataframe: CSVBackTestDataFeed):
    i = ichimoku(dataframe, inplace=True)

    assert math.isnan(i.l.ichimoku_tenkan_sen[0])
    assert math.isnan(i.l.ichimoku_tenkan_sen[7])
    assert not math.isnan(i.l.ichimoku_tenkan_sen[8])
    assert round(i.l.ichimoku_tenkan_sen[8], 6) == 0.977195

    i.l.next(9)

    assert round(i.l.ichimoku_tenkan_sen[0], 6) == 0.977435

    i.l.next(191)

    assert round(i.l.ichimoku_tenkan_sen[0], 6) == 0.990105


def test_kijun_sen(dataframe: CSVBackTestDataFeed):
    i = ichimoku(dataframe, inplace=True)

    assert math.isnan(i.l.ichimoku_kijun_sen[0])
    assert math.isnan(i.l.ichimoku_kijun_sen[24])
    assert not math.isnan(i.l.ichimoku_kijun_sen[25])
    assert round(i.l.ichimoku_kijun_sen[25], 6) == 0.980005

    i.l.next(26)

    assert round(i.l.ichimoku_kijun_sen[0], 6) == 0.980005

    i.l.next(174)

    assert round(i.l.ichimoku_kijun_sen[0], 6) == 0.991940


def test_chikou_span(dataframe: CSVBackTestDataFeed):
    i = ichimoku(dataframe, inplace=True)

    assert not math.isnan(i.l.ichimoku_chikou_span[0])
    assert i.l.ichimoku_chikou_span[0] == i.l.close[25]
    assert i.l.ichimoku_chikou_span[0] == 0.97832

    i.l.next(26)

    assert i.l.ichimoku_chikou_span[-25] == i.l.close[0]
    assert round(i.l.ichimoku_chikou_span[-25], 6) == 0.97784
    assert round(i.l.ichimoku_chikou_span[0], 6) == 0.98494

    i.l.next(174)

    assert round(i.l.ichimoku_chikou_span[0], 6) == 0.98827


def test_senko_span_ab(dataframe: CSVBackTestDataFeed):
    i = ichimoku(dataframe, inplace=True)

    assert math.isnan(i.l.ichimoku_senkou_span_a[0])
    assert math.isnan(i.l.ichimoku_senkou_span_b[0])

    assert math.isnan(i.l.ichimoku_leading_senkou_span_a[24])
    assert math.isnan(i.l.ichimoku_leading_senkou_span_b[50])
    assert math.isnan(i.l.ichimoku_senkou_span_a[24 + 25])
    assert math.isnan(i.l.ichimoku_senkou_span_b[50 + 25])

    assert not math.isnan(i.l.ichimoku_leading_senkou_span_a[25])
    assert not math.isnan(i.l.ichimoku_leading_senkou_span_b[51])
    assert not math.isnan(i.l.ichimoku_senkou_span_a[25 + 25])
    assert not math.isnan(i.l.ichimoku_senkou_span_b[51 + 25])

    i.l.next(52)

    assert round(i.l.ichimoku_senkou_span_a[25], 6) == 0.983183
    assert round(i.l.ichimoku_senkou_span_b[25], 6) == 0.980205

    assert i.l.ichimoku_leading_senkou_span_a[0] == i.l.ichimoku_senkou_span_a[25]
    assert i.l.ichimoku_leading_senkou_span_b[0] == i.l.ichimoku_senkou_span_b[25]

    i.l.next(148)

    assert round(i.l.ichimoku_senkou_span_a[25], 7) == 0.9910225
    assert round(i.l.ichimoku_senkou_span_b[25], 6) == 0.993565

    assert i.l.ichimoku_leading_senkou_span_a[0] == i.l.ichimoku_senkou_span_a[25]
    assert i.l.ichimoku_leading_senkou_span_b[0] == i.l.ichimoku_senkou_span_b[25]
