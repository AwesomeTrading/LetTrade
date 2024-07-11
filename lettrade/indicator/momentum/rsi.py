import pandas as pd
import talib.abstract as ta

from ..series import series_init


def rsi(
    series: pd.Series | str = "close",
    window: int = None,
    dataframe: pd.DataFrame | None = None,
    name: str | None = None,
    prefix: str = "",
    inplace: bool = False,
    plot: bool | list[str] = False,
    plot_kwargs: dict | None = None,
    **kwargs,
) -> pd.Series | pd.DataFrame:
    """_summary_

    Args:
        series (pd.Series | str, optional): _description_. Defaults to "close".
        window (int, optional): _description_. Defaults to None.
        dataframe (pd.DataFrame, optional): _description_. Defaults to None.
        name (str | None, optional): _description_. Defaults to None.
        prefix (str, optional): _description_. Defaults to "".
        inplace (bool, optional): _description_. Defaults to False.
        plot (bool | list, optional): _description_. Defaults to False.
        plot_kwargs (dict | None, optional): _description_. Defaults to None.

    Raises:
        RuntimeError: _description_

    Returns:
        pd.Series | pd.DataFrame: {rsi}
    """
    # Validation & init
    if __debug__:
        if window is None or window <= 0:
            raise RuntimeError(f"Window {window} is invalid")
    series = series_init(series=series, dataframe=dataframe, inplace=inplace)

    # Indicator
    i = ta.RSI(series, timeperiod=window, **kwargs)

    if inplace:
        name = name or f"{prefix}rsi"
        dataframe[name] = i

        # Plot
        if plot:
            if plot_kwargs is None:
                plot_kwargs = dict()

            plot_kwargs.update(series=name, name=name)
            plot_kwargs.setdefault("row", 2)
            plot_kwargs.setdefault("row_height", 0.5)

            from lettrade.indicator.plot import IndicatorPlotter
            from lettrade.plot.plotly import plot_line

            IndicatorPlotter(dataframe=dataframe, plotter=plot_line, **plot_kwargs)

        return dataframe

    return i
