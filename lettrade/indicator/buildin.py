import pandas as pd


def cross(series1: pd.Series, series2: pd.Series, index=0):
    return series1[index] - series2[index]


def above(series1: pd.Series, series2: pd.Series, index=0) -> bool:
    crossed = cross(series1, series2, index=index)
    return crossed > 0


def below(series1: pd.Series, series2: pd.Series, index=0) -> bool:
    crossed = cross(series1, series2, index=index)
    return crossed < 0


def crossover(series1: pd.Series, series2: pd.Series, index=0) -> bool:
    below1 = below(series1, series2, index=index)
    above0 = above(series1, series2, index=index - 1)
    return below1 and above0
