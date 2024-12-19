from typing import Literal

import pandas as pd
import talib.abstract as ta

from lettrade.plot import PlotColor

from ..utils import talib_ma


def keltner_channel(
    dataframe: pd.DataFrame,
    ma: int = 20,
    ma_mode: Literal[
        "sma",
        "ema",
        "wma",
        "dema",
        "tema",
        "trima",
        "kama",
        "mama",
        "t3",
    ] = "ema",
    atr: int = 20,
    shift: float = 1.6,
    prefix: str = "kc_",
    inplace: bool = False,
    plot: bool | list[str] = False,
    plot_upper_kwargs: dict | None = None,
    plot_basis_kwargs: dict | None = None,
    plot_lower_kwargs: dict | None = None,
) -> dict[str, pd.Series] | pd.DataFrame:
    """_summary_

    Args:
        dataframe (pd.DataFrame): _description_
        ma (int, optional): _description_. Defaults to 20.
        ma_mode (Literal[ "sma", "ema", "wma", "dema", "tema", "trima", "kama", "mama", "t3", ], optional): _description_. Defaults to "ema".
        atr (int, optional): _description_. Defaults to 20.
        shift (float, optional): _description_. Defaults to 1.6.
        prefix (str, optional): _description_. Defaults to "kc_".
        inplace (bool, optional): _description_. Defaults to False.
        plot (bool | list[str], optional): _description_. Defaults to False.
        plot_upper_kwargs (dict | None, optional): _description_. Defaults to None.
        plot_basis_kwargs (dict | None, optional): _description_. Defaults to None.
        plot_lower_kwargs (dict | None, optional): _description_. Defaults to None.

    Example:
        ```python
        df.i.keltner_channel(ma=20, atr=20, shift=1.6, inplace=True, plot=True)
        ```

    Raises:
        RuntimeError: _description_

    Returns:
        dict[str, pd.Series] | pd.DataFrame: {kc_upper, kc_middle, kc_lower}
    """
    if __debug__:
        if not isinstance(dataframe, pd.DataFrame):
            raise RuntimeError(
                f"dataframe type '{type(dataframe)}' "
                "is not instance of pandas.DataFrame"
            )
        if plot and not inplace:
            raise RuntimeError("Cannot plot when inplace=False")

    ma_fn = talib_ma(ma_mode)
    i_basis = ma_fn(dataframe, timeperiod=ma)

    i_atr = ta.ATR(dataframe, timeperiod=atr)
    i_upper = i_basis + shift * i_atr
    i_lower = i_basis - shift * i_atr

    # Result is inplace or new dict
    result = dataframe if inplace else {}
    result[f"{prefix}upper"] = i_upper
    result[f"{prefix}basis"] = i_basis
    result[f"{prefix}lower"] = i_lower

    # Plot
    if plot:
        from lettrade.indicator.plot import IndicatorPlotter
        from lettrade.plot.plotly import plot_lines

        # Enable lines
        if isinstance(plot, list):
            # Upper
            if f"{prefix}upper" in plot:
                if plot_upper_kwargs is None:
                    plot_upper_kwargs = dict()
            else:
                plot_upper_kwargs = None

            # Basis
            if f"{prefix}basis" in plot:
                if plot_basis_kwargs is None:
                    plot_basis_kwargs = dict()
            else:
                plot_basis_kwargs = None

            # Lower
            if f"{prefix}lower" in plot:
                if plot_lower_kwargs is None:
                    plot_lower_kwargs = dict()
            else:
                plot_lower_kwargs = None

        else:
            if plot_upper_kwargs is None:
                plot_upper_kwargs = dict()
            if plot_basis_kwargs is None:
                plot_basis_kwargs = dict()
            if plot_lower_kwargs is None:
                plot_lower_kwargs = dict()

        #
        serieses = []
        plots_kwargs = []

        # Upper
        if plot_upper_kwargs is not None:
            plot_upper_kwargs.setdefault("name", f"{prefix}upper")
            plot_upper_kwargs.setdefault("color", PlotColor.CYAN)
            serieses.append(i_upper)
            plots_kwargs.append(plot_upper_kwargs)

        # Basis
        if plot_basis_kwargs is not None:
            plot_basis_kwargs.setdefault("name", f"{prefix}basis")
            plot_basis_kwargs.setdefault("color", PlotColor.AMBER)
            serieses.append(i_basis)
            plots_kwargs.append(plot_basis_kwargs)

        # Lower
        if plot_lower_kwargs is not None:
            plot_lower_kwargs.setdefault("name", f"{prefix}lower")
            plot_lower_kwargs.setdefault("color", PlotColor.PURPLE)
            serieses.append(i_lower)
            plots_kwargs.append(plot_lower_kwargs)

        IndicatorPlotter(
            serieses=serieses,
            dataframe=dataframe,
            plotter=plot_lines,
            name=prefix,
            plots_kwargs=plots_kwargs,
        )

    return result
