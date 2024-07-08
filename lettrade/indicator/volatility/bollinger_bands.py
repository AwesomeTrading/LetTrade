from typing import Literal

import pandas as pd
import talib.abstract as ta

from ..series import series_init
from ..utils import talib_ma_mode


def bollinger_bands(
    series: pd.Series | str = "close",
    window: int = 0,
    std: int | float = 0,
    ma_mode: Literal["ema", "sma"] = "sma",
    dataframe: pd.DataFrame = None,
    prefix: str = "bb_",
    inplace: bool = False,
    plot: bool | list = False,
    plot_kwargs: dict | None = None,
    **kwargs,
) -> dict[str, pd.Series] | pd.DataFrame:
    """_summary_

    Args:
        series (pd.Series | str, optional): _description_. Defaults to "close".
        window (int, optional): _description_. Defaults to 0.
        std (int | float, optional): _description_. Defaults to 0.
        ma_mode (Literal[&quot;ema&quot;, &quot;sma&quot;], optional): _description_. Defaults to "sma".
        dataframe (pd.DataFrame, optional): _description_. Defaults to None.
        prefix (str, optional): _description_. Defaults to "bb_".
        inplace (bool, optional): _description_. Defaults to False.
        plot (bool | list, optional): Flag or list of columns name. Defaults to False.
        plot_kwargs (dict | None, optional): _description_. Defaults to None.

    Example:
        ```python
        df.i.bollinger_bands(window=20, std=2.0, inplace=True, plot=True)
        ```

    Raises:
        RuntimeError: _description_

    Returns:
        dict[str, pd.Series] | pd.DataFrame: _description_
    """
    if __debug__:
        if window <= 0:
            raise RuntimeError(f"Window {window} is invalid")
        if std <= 0:
            raise RuntimeError(f"Std {std} is invalid")
        if plot and not inplace:
            raise RuntimeError("Cannot plot when inplace=False")

    series = series_init(series=series, dataframe=dataframe, inplace=inplace)

    i_upper, i_basis, i_lower = ta.BBANDS(
        series,
        timeperiod=window,
        nbdevup=std,
        nbdevdn=std,
        matype=talib_ma_mode(ma_mode),
        **kwargs,
    )

    # Result is inplace or new dict
    result = dataframe if inplace else {}
    result[f"{prefix}upper"] = i_upper
    result[f"{prefix}basis"] = i_basis
    result[f"{prefix}lower"] = i_lower

    # Plot
    if plot:
        if plot_kwargs is None:
            plot_kwargs = dict()

        if isinstance(plot, list):
            if f"{prefix}upper" in plot:
                plot_kwargs.update(upper=f"{prefix}upper")
            if f"{prefix}basis" in plot:
                plot_kwargs.update(basis=f"{prefix}basis")
            if f"{prefix}lower" in plot:
                plot_kwargs.update(lower=f"{prefix}lower")
        else:
            plot_kwargs.update(
                upper=f"{prefix}upper",
                basis=f"{prefix}basis",
                lower=f"{prefix}lower",
            )

        from lettrade.indicator.plot import IndicatorPlotter
        from lettrade.plot.plotly import plot_bollinger_bands

        IndicatorPlotter(
            dataframe=dataframe,
            plotter=plot_bollinger_bands,
            **plot_kwargs,
        )

    return result
