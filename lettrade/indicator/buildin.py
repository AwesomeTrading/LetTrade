import pandas as pd


def above(series1: pd.Series, series2: pd.Series):
    data = series1 - series2
    return data


def below(series1: pd.Series, series2: pd.Series):
    data = series1 - series2
    return data


def crossover(series1: pd.Series, series2: pd.Series, index=-1):
    return (
        below(series1[index - 1], series2[index - 1])
        and above(series1[index], series2[index]) > 0
    )
