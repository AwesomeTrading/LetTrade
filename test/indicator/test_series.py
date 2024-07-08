import numpy as np
import pandas as pd
import pandas.testing as pdtest
import pytest

from lettrade.indicator import (
    above,
    below,
    crossover,
    crossunder,
    rolling_above,
    rolling_below,
    rolling_max,
    rolling_mean,
    rolling_min,
    s_above,
    s_below,
)


@pytest.fixture
def series1():
    return pd.Series([1] * 5 + [2] * 5 + [1] * 5)


@pytest.fixture
def series2():
    return pd.Series([2] * 5 + [1] * 5 + [4] * 5)


### Test signal
def test_s_above(series1: pd.Series, series2: pd.Series):
    i = s_above(series1, series2)
    values = pd.Series([0] * 5 + [100] * 5 + [0] * 5)

    pdtest.assert_series_equal(i, values)


def test_s_below(series1: pd.Series, series2: pd.Series):
    i = s_below(series1, series2)
    values = pd.Series([-100] * 5 + [0] * 5 + [-100] * 5)

    pdtest.assert_series_equal(i, values)


### Test indicator above/below
def test_above(series1: pd.Series, series2: pd.Series):
    i = above(series1, series2)
    values = pd.Series([0] * 5 + [100] * 5 + [0] * 5)

    pdtest.assert_series_equal(i, values)


def test_below(series1: pd.Series, series2: pd.Series):
    i = below(series1, series2)
    values = pd.Series([-100] * 5 + [0] * 5 + [-100] * 5)

    pdtest.assert_series_equal(i, values)


### Test indicator rolling_above/rolling_below
def test_rolling_above(series1: pd.Series, series2: pd.Series):
    i = rolling_above(series1, series2, window=3)
    values = pd.Series([0] * 5 + [0, 0, 100, 100, 100] + [0] * 5)

    pdtest.assert_series_equal(i, values)


def test_rolling_below(series1: pd.Series, series2: pd.Series):
    i = rolling_below(series1, series2, window=3)
    values = pd.Series([0, 0, -100, -100, -100] + [0] * 5 + [0, 0, -100, -100, -100])

    pdtest.assert_series_equal(i, values)


### Test indicator crossover/crossunder
def test_crossover(series1: pd.Series, series2: pd.Series):
    i = crossover(series1, series2)
    values = pd.Series([0] * 5 + [100] + [0] * 9)

    pdtest.assert_series_equal(i, values)


def test_crossunder(series1: pd.Series, series2: pd.Series):
    i = crossunder(series1, series2)
    values = pd.Series([0] * 10 + [-100] + [0] * 4)

    pdtest.assert_series_equal(i, values)


### Test indicator rolling_min/rolling_max/rolling_mean
def test_rolling_min(series1: pd.Series):
    i = rolling_min(series1, window=3)
    values = pd.Series([np.nan, np.nan, 1, 1, 1] + [1, 1, 2, 2, 2] + [1] * 5)

    pdtest.assert_series_equal(i, values)


def test_rolling_max(series1: pd.Series):
    i = rolling_max(series1, window=3)
    values = pd.Series([np.nan, np.nan, 1, 1, 1] + [2] * 5 + [2, 2, 1, 1, 1])

    pdtest.assert_series_equal(i, values)


def test_rolling_mean(series1: pd.Series):
    i = rolling_mean(series1, window=3)
    values = pd.Series(
        [np.nan, np.nan, 1, 1, 1] + [4 / 3, 5 / 3, 2, 2, 2] + [5 / 3, 4 / 3, 1, 1, 1]
    )

    pdtest.assert_series_equal(i, values)
