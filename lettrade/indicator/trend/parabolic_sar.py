from sys import float_info as sflt

import numpy as np
import pandas as pd


def zero(x: tuple[int, float]) -> tuple[int, float]:
    """If the value is close to zero, then return zero. Otherwise return itself."""
    return 0 if abs(x) < sflt.epsilon else x


def parabolic_sar(
    dataframe: pd.DataFrame,
    af0: float = 0.02,
    af: float = 0.02,
    max_af: float = 0.2,
    prefix: str = "psar_",
    inplace: bool = False,
    plot: bool | list[str] = False,
    plot_kwargs: dict | None = None,
) -> dict[str, pd.Series] | pd.DataFrame:
    """Indicator: Parabolic Stop and Reverse (PSAR)

    Source:
        https://github.com/twopirllc/pandas-ta/blob/main/pandas_ta/trend/psar.py

    Args:
        dataframe (pd.DataFrame): _description_
        af0 (float, optional): _description_. Defaults to 0.02.
        af (float, optional): _description_. Defaults to 0.02.
        max_af (float, optional): _description_. Defaults to 0.2.
        prefix (str, optional): _description_. Defaults to "psar_".
        inplace (bool, optional): _description_. Defaults to False.
        plot (bool | list, optional): _description_. Defaults to False.
        plot_kwargs (dict | None, optional): _description_. Defaults to None.

    Raises:
        RuntimeError: _description_

    Returns:
        dict[str, pd.Series] | pd.DataFrame: _description_
    """
    if __debug__:
        if not isinstance(dataframe, pd.DataFrame):
            raise RuntimeError(
                f"dataframe type '{type(dataframe)}' "
                "is not instance of pandas.DataFrame"
            )

    def _falling(high: pd.Series, low: pd.Series, drift: int = 1):
        """Returns the last -DM value"""
        # Not to be confused with ta.falling()
        up = high - high.shift(drift)
        dn = low.shift(drift) - low
        dmn = (((dn > up) & (dn > 0)) * dn).apply(zero).iloc[-1]
        return dmn > 0

    # Falling if the first NaN -DM is positive
    falling = _falling(dataframe.high.iloc[:2], dataframe.low.iloc[:2])
    if falling:
        sar = dataframe.high.iloc[0]
        ep = dataframe.low.iloc[0]
    else:
        sar = dataframe.low.iloc[0]
        ep = dataframe.high.iloc[0]

    sar = dataframe.close.iloc[0]

    i_long = pd.Series(np.nan, index=dataframe.high.index)
    i_short = i_long.copy()
    i_reversal = pd.Series(0, index=dataframe.high.index)
    i_af = i_long.copy()
    i_af.iloc[0:2] = af0

    # Calculate Result
    m = dataframe.high.shape[0]
    for row in range(1, m):
        high_ = dataframe.high.iloc[row]
        low_ = dataframe.low.iloc[row]

        if falling:
            _sar = sar + af * (ep - sar)
            reverse = high_ > _sar

            if low_ < ep:
                ep = low_
                af = min(af + af0, max_af)

            _sar = max(dataframe.high.iloc[row - 1], dataframe.high.iloc[row - 2], _sar)
        else:
            _sar = sar + af * (ep - sar)
            reverse = low_ < _sar

            if high_ > ep:
                ep = high_
                af = min(af + af0, max_af)

            _sar = min(dataframe.low.iloc[row - 1], dataframe.low.iloc[row - 2], _sar)

        if reverse:
            _sar = ep
            af = af0
            falling = not falling  # Must come before next line
            ep = low_ if falling else high_

        sar = _sar  # Update SAR

        # Seperate long/short sar based on falling
        if falling:
            i_short.iloc[row] = sar
        else:
            i_long.iloc[row] = sar

        i_af.iloc[row] = af
        i_reversal.iloc[row] = int(reverse)

    # Result is inplace or new dict
    result = dataframe if inplace else {}

    result[f"{prefix}long"] = i_long
    result[f"{prefix}short"] = i_short
    result[f"{prefix}af"] = i_af
    result[f"{prefix}reversal"] = i_reversal

    # Plot
    if plot:
        if plot_kwargs is None:
            plot_kwargs = dict()

        if isinstance(plot, list):
            if f"{prefix}long" in plot:
                plot_kwargs.update(long=f"{prefix}long")
            if f"{prefix}short" in plot:
                plot_kwargs.update(short=f"{prefix}short")
        else:
            plot_kwargs.update(
                long=f"{prefix}long",
                short=f"{prefix}short",
            )

        from lettrade.indicator.plot import IndicatorPlotter
        from lettrade.plot.plotly import plot_parabolic_sar

        IndicatorPlotter(
            dataframe=dataframe,
            plotter=plot_parabolic_sar,
            **plot_kwargs,
        )

    return result
