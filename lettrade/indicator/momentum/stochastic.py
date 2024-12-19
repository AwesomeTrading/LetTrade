import pandas as pd
import talib.abstract as ta

from lettrade.plot import PlotColor

from ..series import series_init
from ..utils import talib_ma_mode


def stochastic(
    series: pd.Series | list[str] | str = "close",
    fastk_window=14,
    slowk_window=1,
    slowk_matype="sma",
    slowd_window=3,
    slowd_matype="sma",
    dataframe: pd.DataFrame | None = None,
    prefix: str = "stoch_",
    inplace: bool = False,
    plot: bool | list[str] = False,
    plot_slowk_kwargs: dict | None = None,
    plot_slowd_kwargs: dict | None = None,
    **kwargs,
) -> pd.Series | pd.DataFrame:
    """_summary_

    Args:
        series (pd.Series | list[str] | str, optional): _description_. Defaults to "close".
        fastk_window (int, optional): _description_. Defaults to 14.
        slowk_window (int, optional): _description_. Defaults to 1.
        slowk_matype (str, optional): _description_. Defaults to "sma".
        slowd_window (int, optional): _description_. Defaults to 3.
        slowd_matype (str, optional): _description_. Defaults to "sma".
        dataframe (pd.DataFrame | None, optional): _description_. Defaults to None.
        prefix (str, optional): _description_. Defaults to "".
        inplace (bool, optional): _description_. Defaults to False.
        plot (bool | list[str], optional): _description_. Defaults to False.
        plot_slowk_kwargs (dict | None, optional): _description_. Defaults to None.
        plot_slowd_kwargs (dict | None, optional): _description_. Defaults to None.

    Returns:
        pd.Series | pd.DataFrame: _description_
    """
    # # Validation & init
    # if __debug__:
    #     if window is None or window <= 0:
    #         raise RuntimeError(f"Window {window} is invalid")
    if isinstance(series, str):
        series = ["high", "low", series]
    series = series_init(series=series, dataframe=dataframe, inplace=inplace)

    # Indicator
    slowk, slowd = ta.STOCH(
        *series,
        fastk_period=fastk_window,
        slowk_period=slowk_window,
        slowk_matype=talib_ma_mode(slowk_matype),
        slowd_period=slowd_window,
        slowd_matype=talib_ma_mode(slowd_matype),
        **kwargs,
    )

    result = dataframe if inplace else {}
    result[f"{prefix}slowk"] = slowk
    result[f"{prefix}slowd"] = slowd

    # Plot
    if plot:
        from lettrade.indicator.plot import IndicatorPlotter
        from lettrade.plot.plotly import plot_lines

        # Enable lines
        if isinstance(plot, list):
            # SlowK
            if f"{prefix}slowk" in plot:
                if plot_slowk_kwargs is None:
                    plot_slowk_kwargs = dict()
            else:
                plot_slowk_kwargs = None

            # SlowD
            if f"{prefix}slowd" in plot:
                if plot_slowd_kwargs is None:
                    plot_slowd_kwargs = dict()
            else:
                plot_slowd_kwargs = None
        else:
            if plot_slowk_kwargs is None:
                plot_slowk_kwargs = dict()
            if plot_slowd_kwargs is None:
                plot_slowd_kwargs = dict()

        serieses = []
        plots_kwargs = []

        # SlowK
        if plot_slowk_kwargs is not None:
            plot_slowk_kwargs.setdefault("name", f"{prefix}slowk")
            plot_slowk_kwargs.setdefault("row", 2)
            plot_slowk_kwargs.setdefault("row_height", 0.5)
            plot_slowk_kwargs.setdefault("color", PlotColor.AMBER)
            serieses.append(slowk)
            plots_kwargs.append(plot_slowk_kwargs)

        # SlowD
        if plot_slowd_kwargs is not None:
            plot_slowd_kwargs.setdefault("name", f"{prefix}slowd")
            plot_slowd_kwargs.setdefault("row", 2)
            plot_slowd_kwargs.setdefault("row_height", 0.5)
            plot_slowd_kwargs.setdefault("color", PlotColor.PINK)
            serieses.append(slowd)
            plots_kwargs.append(plot_slowd_kwargs)

        IndicatorPlotter(
            serieses=serieses,
            dataframe=dataframe,
            plotter=plot_lines,
            name=prefix,
            plots_kwargs=plots_kwargs,
        )

    return result
