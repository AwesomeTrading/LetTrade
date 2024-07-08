from typing import Any, Literal

import numpy as np
import pandas as pd


def pandas_inject(obj: object | None = None):
    if obj is None:
        from pandas.core.base import PandasObject

        obj = PandasObject

    obj.signal_direction = signal_direction
    obj.signal_condiction = signal_condiction


def signal_direction(
    dataframe: pd.DataFrame,
    up: pd.Series,
    down: pd.Series,
    name: str,
    value: int = 0,
    value_up: int = 100,
    value_down: int = -100,
    inplace: bool = False,
    plot: bool | list = False,
    plot_type: Literal["line", "mark"] = "line",
    plot_kwargs: dict | None = None,
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
        plot (bool | list, optional): _description_. Defaults to False.
        plot_type (Literal[&quot;line&quot;, &quot;mark&quot;], optional): _description_. Defaults to "line".
        plot_kwargs (dict | None, optional): _description_. Defaults to None.

    Returns:
        pd.Series | pd.DataFrame: _description_
    """
    return signal_condiction(
        dataframe,
        [up, value_up],
        [down, value_down],
        name=name,
        value=value,
        inplace=inplace,
        plot=plot,
        plot_type=plot_type,
        plot_kwargs=plot_kwargs,
        **kwargs,
    )


def signal_condiction(
    dataframe: pd.DataFrame,
    *condictions: list[list[pd.Series | Any]],
    name: str,
    value: int | float = np.nan,
    inplace: bool = False,
    plot: bool | list = False,
    plot_type: Literal["line", "mark"] = "line",
    plot_kwargs: dict | None = None,
    **kwargs,
) -> pd.Series | pd.DataFrame:
    """Define a signal with multiple condiction

    Args:
        dataframe (pd.DataFrame): _description_
        *condictions (list[list[pd.Series | Any]]): Pairs of condiction [`<pandas.Series condiction>`, `<value>`]
        name (str): Name of signal, column name when add to DataFrame with inplace=True.
        value (int, optional): Default value when condiction is not matched. Defaults to 0.
        inplace (bool, optional): _description_. Defaults to False.
        plot (bool | list, optional): _description_. Defaults to False.
        plot_type (Literal[&quot;line&quot;, &quot;mark&quot;], optional): _description_. Defaults to "line".
        plot_kwargs (dict | None, optional): _description_. Defaults to None.

    Usage:
        ```python
        df.i.signal_condiction(
            [df["close"] > df["open"], 100],
            [df["close"] < df["open"], -100],
            name="cdl_direction",
            inplace=True,
            plot=True,
            plot_kwargs=dict(color="green", width=5),
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
        if plot and not inplace:
            raise RuntimeError("Cannot plot when inplace=False")

    s = pd.Series(value, index=dataframe.index, name=name, **kwargs)
    for condiction in condictions:
        s.loc[condiction[0]] = condiction[1]

    if inplace:
        dataframe[name] = s

        # Plot
        if plot:
            if plot_kwargs is None:
                plot_kwargs = dict()

            plot_kwargs.update(series=name, name=name)

            from lettrade.indicator.plot import IndicatorPlotter
            from lettrade.plot.plotly import plot_line, plot_mark

            plotter = plot_mark if plot_type == "mark" else plot_line
            IndicatorPlotter(dataframe=dataframe, plotter=plotter, **plot_kwargs)

        return dataframe

    return s
