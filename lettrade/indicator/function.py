import numpy as np
import pandas as pd


def diff(series1: pd.Series, series2: pd.Series) -> pd.Series:
    return series1 - series2


def above(series1: pd.Series, series2: pd.Series) -> pd.Series:
    diffed = diff(series1, series2)
    return diffed.apply(lambda v: True if v > 0 else False).astype(bool)


def below(series1: pd.Series, series2: pd.Series) -> pd.Series:
    diffed = diff(series1, series2)
    return diffed.apply(lambda v: True if v < 0 else False).astype(bool)


def crossover(series1: pd.Series, series2: pd.Series) -> pd.Series:
    below1 = below(series1.shift(1), series2.shift(1))
    above0 = above(series1, series2)
    return below1 & above0


def crossunder(series1: pd.Series, series2: pd.Series) -> pd.Series:
    above1 = above(series1.shift(1), series2.shift(1))
    below0 = below(series1, series2)
    return below0 & above1
