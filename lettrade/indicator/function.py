import pandas as pd


def pandas_inject():
    from pandas.core.base import PandasObject

    # diff
    def __call_diff(dataframe, *args, **kwargs):
        return diff(*args, **kwargs, dataframe=dataframe)

    PandasObject.diff = __call_diff

    # above
    def __call_above(dataframe, *args, **kwargs):
        return above(*args, **kwargs, dataframe=dataframe)

    PandasObject.above = __call_above

    # below
    def __call_below(dataframe, *args, **kwargs):
        return below(*args, **kwargs, dataframe=dataframe)

    PandasObject.below = __call_below

    # crossover
    def __call_crossover(dataframe, *args, **kwargs):
        return crossover(*args, **kwargs, dataframe=dataframe)

    PandasObject.crossover = __call_crossover

    # crossunder
    def __call_crossunder(dataframe, *args, **kwargs):
        return crossunder(*args, **kwargs, dataframe=dataframe)

    PandasObject.crossunder = __call_crossunder


def diff(series1: pd.Series, series2: pd.Series, **kwargs) -> pd.Series:
    """Difference between 2 series

    Args:
        series1 (pd.Series): _description_
        series2 (pd.Series): _description_

    Returns:
        pd.Series: Diff of 2 series
    """
    return series1 - series2


def above(series1: pd.Series, series2: pd.Series, **kwargs) -> pd.Series:
    """Check a Series is above another Series

    Args:
        series1 (pd.Series): first Series
        series2 (pd.Series): second Series

    Returns:
        pd.Series: True series1 is above series2 else False
    """
    diffed = diff(series1, series2)
    return diffed.apply(lambda v: True if v > 0 else False).astype(bool)


def below(series1: pd.Series, series2: pd.Series, **kwargs) -> pd.Series:
    """Check a Series is below another Series

    Args:
        series1 (pd.Series): first Series
        series2 (pd.Series): second Series

    Returns:
        pd.Series: True series1 is below series2 else False
    """
    diffed = diff(series1, series2)
    return diffed.apply(lambda v: True if v < 0 else False).astype(bool)


def crossover(series1: pd.Series, series2: pd.Series, **kwargs) -> pd.Series:
    """Check if a Series cross over another Series

    Args:
        series1 (pd.Series): first Series
        series2 (pd.Series): second Series

    Returns:
        pd.Series: True if series1 cross over series2 else False
    """
    below1 = below(series1, series2).shift(1)
    above0 = above(series1, series2)
    return below1 & above0


def crossunder(series1: pd.Series, series2: pd.Series, **kwargs) -> pd.Series:
    """Check if a Series cross under another Series

    Args:
        series1 (pd.Series): first Series
        series2 (pd.Series): second Series

    Returns:
        pd.Series: True if series1 cross under series2 else False
    """
    above1 = above(series1, series2).shift(1)
    below0 = below(series1, series2)
    return below0 & above1
