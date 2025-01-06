from typing import Literal

import numpy as np
import pandas as pd

from lettrade.plot import PlotColor


def pandas_inject(obj: object | None = None):
    if obj is None:
        from pandas.core.base import PandasObject

        obj = PandasObject

    obj.signal_direction = signal_direction
    obj.signal_condiction = signal_condiction
    obj.signal_exist = signal_exist
    obj.signal_repeat = signal_repeat


def signal_direction(
    dataframe: pd.DataFrame,
    up: pd.Series,
    down: pd.Series,
    name: str = "direction",
    value: int = 0,
    value_up: int = 100,
    value_down: int = -100,
    inplace: bool = False,
    plot: bool | list[str] = False,
    plot_type: Literal["line", "mark"] = "mark",
    plot_up_kwargs: dict | None = None,
    plot_down_kwargs: dict | None = None,
    **kwargs,
) -> pd.Series | pd.DataFrame:
    """Define a signal with 2 direction Up and Down with fixed value

    Args:
        dataframe (pd.DataFrame): _description_
        up (pd.Series): _description_
        down (pd.Series): _description_
        name (str): Name of signal, column name when add to DataFrame with inplace=True.
        value (int, optional): Default value when condiction is not matched. Defaults to 0.
        value_up (int, optional): _description_. Defaults to 100.
        value_down (int, optional): _description_. Defaults to -100.
        inplace (bool, optional): Whether to add to the DataFrame and return DataFrame rather than return result. Defaults to False.
        plot (bool | list[str], optional): _description_. Defaults to False.
        plot_type (Literal["line", "mark"], optional): _description_. Defaults to "mark".
        plot_up_kwargs (dict | None, optional): _description_. Defaults to None.
        plot_down_kwargs (dict | None, optional): _description_. Defaults to None.

    Returns:
        pd.Series | pd.DataFrame: _description_
    """

    # Up
    if plot_up_kwargs is None:
        plot_up_kwargs = dict()
    plot_up_kwargs.setdefault("color", PlotColor.CYAN)

    # Down
    if plot_down_kwargs is None:
        plot_down_kwargs = dict()
    plot_down_kwargs.setdefault("color", PlotColor.ORANGE)

    return signal_condiction(
        dataframe=dataframe,
        condictions=[
            dict(
                series=up,
                value=value_up,
                name=f"{name}_up",
                plot_kwargs=plot_up_kwargs,
            ),
            dict(
                series=down,
                value=value_down,
                name=f"{name}_down",
                plot_kwargs=plot_down_kwargs,
            ),
        ],
        name=name,
        value=value,
        inplace=inplace,
        plot=plot,
        plot_type=plot_type,
        **kwargs,
    )


def signal_condiction(
    dataframe: pd.DataFrame,
    condictions: list[dict],
    name: str,
    value: int | float = np.nan,
    inplace: bool = False,
    plot: bool | list[str] = False,
    plot_type: Literal["line", "mark"] = "mark",
    **kwargs,
) -> pd.Series | pd.DataFrame:
    """Define a signal with multiple condiction

    Args:
        dataframe (pd.DataFrame): _description_
        condictions (list[list[pd.Series | Any]]): Pairs of condiction [`<pandas.Series condiction>`, `<value>`]
        name (str): Name of signal, column name when add to DataFrame with inplace=True.
        value (int, optional): Default value when condiction is not matched. Defaults to 0.
        inplace (bool, optional): _description_. Defaults to False.
        plot (bool | list, optional): _description_. Defaults to False.
        plot_type (Literal["line", "mark"], optional): _description_. Defaults to "line".

    Usage:
        ```python
        df.i.signal_condiction(
            [df["close"] > df["open"], 100],
            [df["close"] < df["open"], -100],
            name="cdl_direction",
            inplace=True,
            plot=True,
        )
        ```

    Raises:
        RuntimeError: _description_

    Returns:
        pd.Series | pd.DataFrame: _description_
    """
    if __debug__:
        if not isinstance(dataframe, pd.DataFrame):
            raise RuntimeError(
                f"dataframe type '{type(dataframe)}' "
                "is not instance of pandas.DataFrame"
            )

    # Series
    indicators = []
    plots = {}
    for condiction in condictions:
        series_value = pd.to_numeric(condiction["value"], errors="coerce")
        series_index = dataframe.loc[condiction["series"]].index
        series = pd.Series(
            series_value,
            index=series_index,
            name=condiction["name"],
            **kwargs,
        )
        indicators.append(series)

        if plot and "plot_kwargs" in condiction:
            plots[condiction["name"]] = condiction["plot_kwargs"]

    # Plot
    if plot:
        from lettrade.indicator.plot import IndicatorPlotter
        from lettrade.plot.plotly import plot_line, plot_mark

        for series in indicators:
            if series.name not in plots:
                continue

            plot_kwargs = plots[series.name]
            plot_kwargs.update(series=series, name=series.name)

            plotter = plot_mark if plot_type == "mark" else plot_line
            IndicatorPlotter(dataframe=dataframe, plotter=plotter, **plot_kwargs)

    # Merge
    series = pd.Series(value, index=dataframe.index, name=name, **kwargs)
    for s in indicators:
        series.update(s)

    if inplace:
        dataframe[name] = series
        return dataframe

    return series


def signal_exist(
    dataframe: pd.DataFrame,
    series: pd.Series,
    window: int,
    value_exist_up: int = 100,
    value_exist_down: int = -100,
    name: str = "exist",
    value_up: int = 100,
    value_down: int = -100,
    inplace: bool = False,
    plot: bool | list[str] = False,
    plot_up_kwargs: dict | None = None,
    plot_down_kwargs: dict | None = None,
    **kwargs,
) -> pd.Series | pd.DataFrame:
    """_summary_

    Args:
        dataframe (pd.DataFrame): _description_
        series (pd.Series): _description_
        window (int): _description_
        value_exist_up (int, optional): _description_. Defaults to 100.
        value_exist_down (int, optional): _description_. Defaults to -100.
        name (str, optional): _description_. Defaults to "exist".
        value_up (int, optional): _description_. Defaults to 100.
        value_down (int, optional): _description_. Defaults to -100.
        inplace (bool, optional): _description_. Defaults to False.
        plot (bool | list[str], optional): _description_. Defaults to False.
        plot_up_kwargs (dict | None, optional): _description_. Defaults to None.
        plot_down_kwargs (dict | None, optional): _description_. Defaults to None.

    Returns:
        pd.Series | pd.DataFrame: _description_
    """
    up_rolling_max = series.rolling(window=window).max()
    down_rolling_min = series.rolling(window=window).min()

    signal = signal_direction(
        dataframe=dataframe,
        up=(up_rolling_max >= value_exist_up),
        down=(down_rolling_min <= value_exist_down),
        name=name,
        value_up=value_up,
        value_down=value_down,
        inplace=inplace,
        plot=plot,
        plot_up_kwargs=plot_up_kwargs,
        plot_down_kwargs=plot_down_kwargs,
        **kwargs,
    )
    return signal


def signal_repeat(
    dataframe: pd.DataFrame,
    series: pd.Series,
    window: int,
    value_repeat_up: int = 100,
    value_repeat_down: int = -100,
    name: str = "repeat",
    value_up: int = 100,
    value_down: int = -100,
    inplace: bool = False,
    plot: bool | list[str] = False,
    plot_up_kwargs: dict | None = None,
    plot_down_kwargs: dict | None = None,
    **kwargs,
) -> pd.Series | pd.DataFrame:
    """_summary_

    Args:
        dataframe (pd.DataFrame): _description_
        series (pd.Series): _description_
        window (int): _description_
        value_repeat_up (int, optional): _description_. Defaults to 100.
        value_repeat_down (int, optional): _description_. Defaults to -100.
        name (str, optional): _description_. Defaults to "repeat".
        value_up (int, optional): _description_. Defaults to 100.
        value_down (int, optional): _description_. Defaults to -100.
        inplace (bool, optional): _description_. Defaults to False.
        plot (bool | list[str], optional): _description_. Defaults to False.
        plot_up_kwargs (dict | None, optional): _description_. Defaults to None.
        plot_down_kwargs (dict | None, optional): _description_. Defaults to None.

    Returns:
        pd.Series | pd.DataFrame: _description_
    """
    up_rolling_min = series.rolling(window=window).min()
    down_rolling_max = series.rolling(window=window).max()

    signal = signal_direction(
        up=(up_rolling_min >= value_repeat_up),
        down=(down_rolling_max <= value_repeat_down),
        dataframe=dataframe,
        name=name,
        value_up=value_up,
        value_down=value_down,
        inplace=inplace,
        plot=plot,
        plot_up_kwargs=plot_up_kwargs,
        plot_down_kwargs=plot_down_kwargs,
        **kwargs,
    )
    return signal
