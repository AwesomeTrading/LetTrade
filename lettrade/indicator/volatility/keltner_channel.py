from typing import Literal

import pandas as pd
import talib.abstract as ta

from ..utils import talib_ma


def keltner_channel(
    dataframe: pd.DataFrame,
    ma: int = 20,
    ma_mode: Literal[
        "sma", "ema", "wma", "dema", "tema", "trima", "kama", "mama", "t3"
    ] = "ema",
    atr: int = 20,
    shift: float = 1.6,
    prefix: str = "kc_",
    inplace: bool = False,
    plot: bool | list = False,
    plot_kwargs: dict | None = None,
) -> dict[str, pd.Series] | pd.DataFrame:
    """_summary_

    Args:
        dataframe (pd.DataFrame): _description_
        ma (int, optional): _description_. Defaults to 20.
        ma_mode (Literal[ "sma", "ema", "wma", "dema", "tema", "trima", "kama", "mama", "t3" ], optional): _description_. Defaults to "ema".
        atr (int, optional): _description_. Defaults to 20.
        shift (float, optional): _description_. Defaults to 1.6.
        prefix (str, optional): _description_. Defaults to "kc_".
        inplace (bool, optional): _description_. Defaults to False.
        plot (bool | list, optional): _description_. Defaults to False.
        plot_kwargs (dict | None, optional): _description_. Defaults to None.

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
        from lettrade.plot.plotly import plot_keltner_channel

        IndicatorPlotter(
            dataframe=dataframe,
            plotter=plot_keltner_channel,
            **plot_kwargs,
        )

    return result
