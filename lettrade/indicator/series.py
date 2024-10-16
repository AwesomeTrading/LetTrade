import pandas as pd


def series_init(
    series: pd.Series | str = "close",
    dataframe: pd.DataFrame | None = None,
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
    obj.direction = series_indicator_inject(direction)
    obj.rolling_above = series_indicator_inject(rolling_above)
    obj.rolling_below = series_indicator_inject(rolling_below)
    obj.rolling_direction = series_indicator_inject(rolling_direction)
    obj.rolling_min = series_indicator_inject(rolling_min)
    obj.rolling_max = series_indicator_inject(rolling_max)
    obj.rolling_mean = series_indicator_inject(rolling_mean)
    obj.crossover = series_indicator_inject(crossover)
    obj.crossunder = series_indicator_inject(crossunder)


def diff(
    series1: pd.Series | str,
    series2: pd.Series | str,
    dataframe: pd.DataFrame = None,
    name: str | None = None,
    prefix: str = "",
    inplace: bool = False,
    plot: bool | list[str] = False,
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


def s_above(series1: pd.Series, series2: pd.Series) -> pd.Series:
    return (series1 - series2).apply(lambda v: 100 if v > 0 else 0)


def s_below(series1: pd.Series, series2: pd.Series) -> pd.Series:
    return (series1 - series2).apply(lambda v: -100 if v < 0 else 0)


def s_direction(series1: pd.Series, series2: pd.Series) -> pd.Series:
    return (series1 - series2).apply(lambda v: -100 if v < 0 else 100 if v > 0 else 0)


def above(
    series1: pd.Series | str,
    series2: pd.Series | str,
    dataframe: pd.DataFrame = None,
    name: str | None = None,
    prefix: str = "",
    inplace: bool = False,
    plot: bool | list[str] = False,
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

    i = s_above(series1=series1, series2=series2)

    if inplace:
        name = name or f"{prefix}above"
        dataframe[name] = i

        if plot:
            _plot_mark(dataframe=dataframe, name=name, plot_kwargs=plot_kwargs)

    return i


def below(
    series1: pd.Series | str,
    series2: pd.Series | str,
    dataframe: pd.DataFrame = None,
    name: str | None = None,
    prefix: str = "",
    inplace: bool = False,
    plot: bool | list[str] = False,
    plot_kwargs: dict | None = None,
    # **kwargs,
) -> pd.Series:
    """Check a Series is below another Series

    Args:
        series1 (pd.Series): first Series
        series2 (pd.Series): second Series

    Returns:
        pd.Series: -100 series1 is below series2 else 0
    """
    if __debug__:
        if plot and not inplace:
            raise RuntimeError("Cannot plot when inplace=False")

    if isinstance(series1, str):
        series1 = dataframe[series1]
    if isinstance(series2, str):
        series2 = dataframe[series2]

    i = s_below(series1, series2)

    if inplace:
        name = name or f"{prefix}below"
        dataframe[name] = i

        if plot:
            _plot_mark(dataframe=dataframe, name=name, plot_kwargs=plot_kwargs)

    return i


def direction(
    series1: pd.Series | str,
    series2: pd.Series | str,
    dataframe: pd.DataFrame = None,
    name: str | None = None,
    prefix: str = "",
    inplace: bool = False,
    plot: bool | list[str] = False,
    plot_kwargs: dict | None = None,
    # **kwargs,
) -> pd.Series:
    """Check a Series is direction another Series

    Args:
        series1 (pd.Series): first Series
        series2 (pd.Series): second Series

    Returns:
        pd.Series: -100 if series1 < series2, 100 if series1 > series2, else 0
    """
    if __debug__:
        if plot and not inplace:
            raise RuntimeError("Cannot plot when inplace=False")

    if isinstance(series1, str):
        series1 = dataframe[series1]
    if isinstance(series2, str):
        series2 = dataframe[series2]

    i = s_direction(series1, series2)

    if inplace:
        name = name or f"{prefix}direction"
        dataframe[name] = i

        if plot:
            _plot_mark(dataframe=dataframe, name=name, plot_kwargs=plot_kwargs)

    return i


def rolling_above(
    series1: pd.Series,
    series2: pd.Series,
    window: int = 20,
    min_periods: int | None = None,
    dataframe: pd.DataFrame = None,
    name: str | None = None,
    prefix: str = "",
    inplace: bool = False,
    plot: bool | list[str] = False,
    plot_kwargs: dict | None = None,
    # **kwargs,
) -> pd.Series:
    """Check a Series is rolling above another Series

    Args:
        series1 (pd.Series): first Series
        series2 (pd.Series): second Series

    Returns:
        pd.Series: 100 mean series1 is rolling above series2 else 0
    """
    if __debug__:
        if plot and not inplace:
            raise RuntimeError("Cannot plot when inplace=False")

    if isinstance(series1, str):
        series1 = dataframe[series1]
    if isinstance(series2, str):
        series2 = dataframe[series2]

    min_periods = window if min_periods is None else min_periods

    i = s_above(series1, series2)
    i = i.rolling(window=window, min_periods=min_periods).min()
    i = i.apply(lambda v: 100 if v >= 100 else 0).astype(int)

    if inplace:
        name = name or f"{prefix}rolling_above"
        dataframe[name] = i

        if plot:
            _plot_mark(dataframe=dataframe, name=name, plot_kwargs=plot_kwargs)

    return i


def rolling_below(
    series1: pd.Series,
    series2: pd.Series,
    window: int = 20,
    min_periods: int | None = None,
    dataframe: pd.DataFrame = None,
    name: str | None = None,
    prefix: str = "",
    inplace: bool = False,
    plot: bool | list[str] = False,
    plot_kwargs: dict | None = None,
    # **kwargs,
) -> pd.Series:
    """Check a Series is rolling below another Series

    Args:
        series1 (pd.Series): first Series
        series2 (pd.Series): second Series

    Returns:
        pd.Series: -100 mean series1 is rolling below series2 else 0
    """
    if __debug__:
        if plot and not inplace:
            raise RuntimeError("Cannot plot when inplace=False")

    if isinstance(series1, str):
        series1 = dataframe[series1]
    if isinstance(series2, str):
        series2 = dataframe[series2]

    min_periods = window if min_periods is None else min_periods

    i = s_below(series1, series2)
    i = i.rolling(window=window, min_periods=min_periods).max()
    i = i.apply(lambda v: -100 if v <= -100 else 0).astype(int)

    if inplace:
        name = name or f"{prefix}rolling_below"
        dataframe[name] = i

        if plot:
            _plot_mark(dataframe=dataframe, name=name, plot_kwargs=plot_kwargs)

    return i


def rolling_direction(
    series1: pd.Series,
    series2: pd.Series,
    window: int = 20,
    min_periods: int | None = None,
    dataframe: pd.DataFrame = None,
    name: str | None = None,
    prefix: str = "",
    inplace: bool = False,
    plot: bool | list[str] = False,
    plot_kwargs: dict | None = None,
    # **kwargs,
) -> pd.Series:
    """Check a Series is rolling on one side with another Series

    Args:
        series1 (pd.Series): first Series
        series2 (pd.Series): second Series

    Returns:
        pd.Series:  100 mean series1 keep consistences above series2 at least `window` bars
                    -100 mean series1 keep consistences below series2 at least `window` bars
                    0 else cases
    """
    if __debug__:
        if plot and not inplace:
            raise RuntimeError("Cannot plot when inplace=False")

    if isinstance(series1, str):
        series1 = dataframe[series1]
    if isinstance(series2, str):
        series2 = dataframe[series2]

    min_periods = window if min_periods is None else min_periods

    i = s_direction(series1, series2)
    i = i.rolling(window=window, min_periods=min_periods).mean()
    i = i.apply(lambda v: -100 if v <= -100 else 100 if v >= 100 else 0).astype(int)

    if inplace:
        name = name or f"{prefix}rolling_direction"
        dataframe[name] = i

        if plot:
            _plot_mark(dataframe=dataframe, name=name, plot_kwargs=plot_kwargs)

    return i


def rolling_min(
    series: pd.Series,
    window: int = 14,
    min_periods: int | None = None,
    dataframe: pd.DataFrame = None,
    name: str | None = None,
    prefix: str = "",
    inplace: bool = False,
):
    if isinstance(series, str):
        series = dataframe[series]

    min_periods = window if min_periods is None else min_periods
    i = series.rolling(window=window, min_periods=min_periods).min()

    if inplace:
        name = name or f"{prefix}rolling_min"
        dataframe[name] = i

    return i


def rolling_max(
    series: pd.Series,
    window: int = 14,
    min_periods: int | None = None,
    dataframe: pd.DataFrame = None,
    name: str | None = None,
    prefix: str = "",
    inplace: bool = False,
):
    if isinstance(series, str):
        series = dataframe[series]

    min_periods = window if min_periods is None else min_periods
    i = series.rolling(window=window, min_periods=min_periods).max()

    if inplace:
        name = name or f"{prefix}rolling_max"
        dataframe[name] = i

    return i


def rolling_mean(
    series: pd.Series,
    window: int = 14,
    min_periods: int | None = None,
    dataframe: pd.DataFrame = None,
    name: str | None = None,
    prefix: str = "",
    inplace: bool = False,
):
    if isinstance(series, str):
        series = dataframe[series]

    min_periods = window if min_periods is None else min_periods
    i = series.rolling(window=window, min_periods=min_periods).mean()

    if inplace:
        name = name or f"{prefix}rolling_mean"
        dataframe[name] = i

    return i


def crossover(
    series1: pd.Series | str,
    series2: pd.Series | str,
    dataframe: pd.DataFrame = None,
    name: str | None = None,
    prefix: str = "",
    inplace: bool = False,
    plot: bool | list[str] = False,
    plot_kwargs: dict | None = None,
    # **kwargs,
) -> pd.Series:
    """Check if a Series cross over another Series

    Args:
        series1 (pd.Series): first Series
        series2 (pd.Series): second Series

    Returns:
        pd.Series: 100 if series1 cross over series2 else 0
    """
    if __debug__:
        if plot and not inplace:
            raise RuntimeError("Cannot plot when inplace=False")

    if isinstance(series1, str):
        series1 = dataframe[series1]
    if isinstance(series2, str):
        series2 = dataframe[series2]

    below1 = s_below(series1, series2).shift(1)
    above0 = s_above(series1, series2)
    i = (-below1 + above0).apply(lambda v: 100 if v >= 200 else 0)

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
    plot: bool | list[str] = False,
    plot_kwargs: dict | None = None,
    # **kwargs,
) -> pd.Series:
    """Check if a Series cross under another Series

    Args:
        series1 (pd.Series): first Series
        series2 (pd.Series): second Series

    Returns:
        pd.Series: -100 if series1 cross under series2 else 0
    """
    if __debug__:
        if plot and not inplace:
            raise RuntimeError("Cannot plot when inplace=False")

    if isinstance(series1, str):
        series1 = dataframe[series1]
    if isinstance(series2, str):
        series2 = dataframe[series2]

    above1 = s_above(series1, series2).shift(1)
    below0 = s_below(series1, series2)
    i = (below0 - above1).apply(lambda v: -100 if v <= -200 else 0)

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
