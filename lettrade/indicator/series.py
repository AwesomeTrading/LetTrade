import pandas as pd


def series_init(
    series: pd.Series | str = "close",
    dataframe: pd.DataFrame = None,
    inplace: bool = False,
):

    if dataframe is None:
        if __debug__:
            if not isinstance(series, pd.Series):
                raise RuntimeError(
                    f"Series type '{type(series)}' is not instance of pandas.Series"
                )

            if inplace:
                raise RuntimeError("DataFrame isnot set when inplace=True")
    else:
        if __debug__:
            if not isinstance(dataframe, pd.DataFrame):
                raise RuntimeError(
                    f"DataFrame type '{type(dataframe)}' "
                    "is not instance of pandas.DataFrame"
                )

            if not isinstance(series, str):
                raise RuntimeError(
                    f"Series type {type(series)} is not string of column name"
                )

        series = dataframe[series]
    return series


def series_indicator_inject(fn):
    def __call(data, *args, **kwargs):
        if isinstance(data, pd.DataFrame):
            return fn(*args, **kwargs, dataframe=data)

        if isinstance(data, pd.Series):
            return fn(data, *args, **kwargs)

        raise RuntimeError(f"Indicator parameter type {type(data)} is invalid")

    return __call


def pandas_inject(obj: object | None = None):
    if obj is None:
        from pandas.core.base import PandasObject

        obj = PandasObject

    obj.diff = series_indicator_inject(diff)
    obj.above = series_indicator_inject(above)
    obj.below = series_indicator_inject(below)
    obj.crossover = series_indicator_inject(crossover)
    obj.crossunder = series_indicator_inject(crossunder)


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
