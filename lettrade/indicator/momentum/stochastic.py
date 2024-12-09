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
        pd.Series | pd.DataFrame: {stochastic}
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

    if inplace:
        name = name or f"{prefix}stochastic"
        dataframe[f"{name}_slowk"] = slowk
        dataframe[f"{name}_slowd"] = slowd

        # Plot
        if plot:
            if plot_kwargs is None:
                plot_kwargs = dict()

            # plot_kwargs.update(series=name, name=name)
            plot_kwargs.setdefault("row", 2)
            plot_kwargs.setdefault("row_height", 0.5)

            from lettrade.indicator.plot import IndicatorPlotter
            from lettrade.plot.plotly import plot_lines

            IndicatorPlotter(
                serieses=[f"{name}_slowk", f"{name}_slowd"],
                dataframe=dataframe,
                plotter=plot_lines,
                name=name,
                plots_kwargs=[
                    dict(
                        name=f"{name}_slowk",
                        color=PlotColor.AMBER,
                    ),
                    dict(
                        name=f"{name}_slowd",
                        color=PlotColor.BLUE,
                    ),
                ],
                **plot_kwargs,
            )

        return dataframe

    return slowk, slowd
