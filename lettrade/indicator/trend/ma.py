from typing import Literal

import pandas as pd

from ..series import series_init
from ..utils import talib_ma


def ema(
    series: pd.Series | str = "close",
    window: int = None,
    dataframe: pd.DataFrame = None,
    name: str | None = None,
    prefix: str = "",
    inplace: bool = False,
    plot: bool | list = False,
    plot_kwargs: dict | None = None,
    **kwargs,
) -> pd.Series | pd.DataFrame:
    """Exponential Moving Average

    Args:
        series (pd.Series | str, optional): _description_. Defaults to "close".
        window (int, optional): _description_. Defaults to None.
        dataframe (pd.DataFrame, optional): _description_. Defaults to None.
        name (str | None, optional): _description_. Defaults to None.
        prefix (str, optional): _description_. Defaults to "".
        inplace (bool, optional): _description_. Defaults to False.
        plot (bool | list, optional): _description_. Defaults to False.
        plot_kwargs (dict | None, optional): _description_. Defaults to None.

    Example:
        ```python
        df.i.ema(window=21, name="ema", inplace=True, plot=True)
        ```

    Returns:
        pd.Series | pd.DataFrame: _description_
    """
    return ma(
        series=series,
        window=window,
        mode="ema",
        dataframe=dataframe,
        name=name,
        prefix=prefix,
        inplace=inplace,
        plot=plot,
        plot_kwargs=plot_kwargs,
        **kwargs,
    )


def ma(
    series: pd.Series | str = "close",
    window: int = None,
    mode: Literal[
        "sma", "ema", "wma", "dema", "tema", "trima", "kama", "mama", "t3"
    ] = None,
    dataframe: pd.DataFrame = None,
    name: str | None = None,
    prefix: str = "",
    inplace: bool = False,
    plot: bool | list = False,
    plot_kwargs: dict | None = None,
    **kwargs,
) -> pd.Series | pd.DataFrame:
    """Moving Average

    Args:
        series (pd.Series | str, optional): _description_. Defaults to "close".
        window (int, optional): _description_. Defaults to None.
        mode (Literal[ &quot;sma&quot;, &quot;ema&quot;, &quot;wma&quot;, &quot;dema&quot;, &quot;tema&quot;, &quot;trima&quot;, &quot;kama&quot;, &quot;mama&quot;, &quot;t3&quot; ], optional): _description_. Defaults to None.
        dataframe (pd.DataFrame, optional): _description_. Defaults to None.
        name (str | None, optional): _description_. Defaults to None.
        prefix (str, optional): _description_. Defaults to "".
        inplace (bool, optional): _description_. Defaults to False.
        plot (bool | list, optional): _description_. Defaults to False.
        plot_kwargs (dict | None, optional): _description_. Defaults to None.

    Example:
        ```python
        df.i.ma(window=21, name="sma", mode="sma", inplace=True, plot=True)
        ```

    Raises:
        RuntimeError: _description_

    Returns:
        pd.Series | pd.DataFrame: _description_
    """
    # Validation & init
    if __debug__:
        if window is None or window <= 0:
            raise RuntimeError(f"Window {window} is invalid")
        if mode is None:
            raise RuntimeError(f"Mode {window} is invalid")
        if plot and not inplace:
            raise RuntimeError("Cannot plot when inplace=False")

    series = series_init(series=series, dataframe=dataframe, inplace=inplace)

    # Indicator
    ma_fn = talib_ma(mode)
    i = ma_fn(series, timeperiod=window, **kwargs)

    if inplace:
        name = name or f"{prefix}{mode}"
        dataframe[name] = i

        # Plot
        if plot:
            if plot_kwargs is None:
                plot_kwargs = dict()

            plot_kwargs.update(series=name, name=name)

            from lettrade.indicator.plot import IndicatorPlotter
            from lettrade.plot.plotly import plot_line

            IndicatorPlotter(dataframe=dataframe, plotter=plot_line, **plot_kwargs)

        return dataframe

    return i
