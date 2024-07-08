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


def diff(
    series1: pd.Series,
    series2: pd.Series,
    dataframe: pd.DataFrame = None,
    name: str | None = None,
    prefix: str = "",
    inplace: bool = False,
    plot: bool | list = False,
    plot_kwargs: dict | None = None,
    # **kwargs,
) -> pd.Series:
    """Difference between 2 series

    Args:
        series1 (pd.Series): _description_
        series2 (pd.Series): _description_
        dataframe (pd.DataFrame, optional): _description_. Defaults to None.
        name (str | None, optional): _description_. Defaults to None.
        prefix (str, optional): _description_. Defaults to "".
        inplace (bool, optional): _description_. Defaults to False.
        plot (bool | list, optional): _description_. Defaults to False.
        plot_kwargs (dict | None, optional): _description_. Defaults to None.

    Raises:
        RuntimeError: _description_

    Returns:
        pd.Series: Difference of 2 series (series1 - series2)
    """
    if __debug__:
        if plot and not inplace:
            raise RuntimeError("Cannot plot when inplace=False")

    if isinstance(series1, str):
        series1 = dataframe[series1]
    if isinstance(series2, str):
        series2 = dataframe[series2]

    i = series1 - series2

    if inplace:
        name = name or f"{prefix}diff"
        dataframe[name] = i

        if plot:
            _plot_mark(dataframe=dataframe, name=name, plot_kwargs=plot_kwargs)

    return i


def above(
    series1: pd.Series,
    series2: pd.Series,
    dataframe: pd.DataFrame = None,
    name: str | None = None,
    prefix: str = "",
    inplace: bool = False,
    plot: bool | list = False,
    plot_kwargs: dict | None = None,
    # **kwargs,
) -> pd.Series:
    """Check a Series is above another Series

    Args:
        series1 (pd.Series): first Series
        series2 (pd.Series): second Series

    Returns:
        pd.Series: True series1 is above series2 else False
    """
    if __debug__:
        if plot and not inplace:
            raise RuntimeError("Cannot plot when inplace=False")

    if isinstance(series1, str):
        series1 = dataframe[series1]
    if isinstance(series2, str):
        series2 = dataframe[series2]

    i = (series1 - series2).apply(lambda v: 100 if v > 0 else 0)

    if inplace:
        name = name or f"{prefix}above"
        dataframe[name] = i

        if plot:
            _plot_mark(dataframe=dataframe, name=name, plot_kwargs=plot_kwargs)

    return i


def below(
    series1: pd.Series,
    series2: pd.Series,
    dataframe: pd.DataFrame = None,
    name: str | None = None,
    prefix: str = "",
    inplace: bool = False,
    plot: bool | list = False,
    plot_kwargs: dict | None = None,
    # **kwargs,
) -> pd.Series:
    """Check a Series is below another Series

    Args:
        series1 (pd.Series): first Series
        series2 (pd.Series): second Series

    Returns:
        pd.Series: True series1 is below series2 else False
    """
    if __debug__:
        if plot and not inplace:
            raise RuntimeError("Cannot plot when inplace=False")

    if isinstance(series1, str):
        series1 = dataframe[series1]
    if isinstance(series2, str):
        series2 = dataframe[series2]

    i = (series1 - series2).apply(lambda v: 100 if v < 0 else 0)

    if inplace:
        name = name or f"{prefix}below"
        dataframe[name] = i

        if plot:
            _plot_mark(dataframe=dataframe, name=name, plot_kwargs=plot_kwargs)

    return i


def crossover(
    series1: pd.Series | str,
    series2: pd.Series | str,
    dataframe: pd.DataFrame = None,
    name: str | None = None,
    prefix: str = "",
    inplace: bool = False,
    plot: bool | list = False,
    plot_kwargs: dict | None = None,
    # **kwargs,
) -> pd.Series:
    """Check if a Series cross over another Series

    Args:
        series1 (pd.Series): first Series
        series2 (pd.Series): second Series

    Returns:
        pd.Series: True if series1 cross over series2 else False
    """
    if __debug__:
        if plot and not inplace:
            raise RuntimeError("Cannot plot when inplace=False")

    if isinstance(series1, str):
        series1 = dataframe[series1]
    if isinstance(series2, str):
        series2 = dataframe[series2]

    below1 = below(series1, series2).shift(1)
    above0 = above(series1, series2)
    i = (below1 + above0).apply(lambda v: 100 if v >= 200 else 0)

    if inplace:
        name = name or f"{prefix}crossover"
        dataframe[name] = i

        if plot:
            _plot_mark(dataframe=dataframe, name=name, plot_kwargs=plot_kwargs)

    return i


def crossunder(
    series1: pd.Series | str,
    series2: pd.Series | str,
    dataframe: pd.DataFrame = None,
    name: str | None = None,
    prefix: str = "",
    inplace: bool = False,
    plot: bool | list = False,
    plot_kwargs: dict | None = None,
    # **kwargs,
) -> pd.Series:
    """Check if a Series cross under another Series

    Args:
        series1 (pd.Series): first Series
        series2 (pd.Series): second Series

    Returns:
        pd.Series: True if series1 cross under series2 else False
    """
    if __debug__:
        if plot and not inplace:
            raise RuntimeError("Cannot plot when inplace=False")

    if isinstance(series1, str):
        series1 = dataframe[series1]
    if isinstance(series2, str):
        series2 = dataframe[series2]

    above1 = above(series1, series2).shift(1)
    below0 = below(series1, series2)
    i = (below0 + above1).apply(lambda v: 100 if v >= 200 else 0)

    if inplace:
        name = name or f"{prefix}crossunder"
        dataframe[name] = i

        if plot:
            _plot_mark(dataframe=dataframe, name=name, plot_kwargs=plot_kwargs)

    return i


def _plot_mark(
    dataframe: pd.DataFrame = None,
    name: str | None = None,
    plot_kwargs: dict | None = None,
):
    if plot_kwargs is None:
        plot_kwargs = dict()

    plot_kwargs.update(series="close", name=name)

    from lettrade.indicator.plot import IndicatorPlotter
    from lettrade.plot.plotly import plot_mark

    IndicatorPlotter(
        dataframe=dataframe,
        plotter=plot_mark,
        filter=lambda df: df[name] != 0,
        **plot_kwargs,
    )
