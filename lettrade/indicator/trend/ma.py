from typing import Literal

import pandas as pd
import talib.abstract as ta

from ..series import series_init
from ..utils import talib_ma


def ema(
    series: pd.Series | str = "close",
    period: int = None,
    dataframe: pd.DataFrame = None,
    prefix: str = "",
    inplace: bool = False,
    **kwargs,
) -> pd.Series | pd.DataFrame:
    """Exponential Moving Average

    Args:
        series (pd.Series | str): _description_
        period (int): _description_
        dataframe (pd.DataFrame, optional): _description_. Defaults to None.
        prefix (str, optional): _description_. Defaults to "".
        inplace (bool, optional): _description_. Defaults to False.

    Raises:
        RuntimeError: _description_

    Returns:
        pd.Series | pd.DataFrame: _description_
    """
    return ma(
        series=series,
        period=period,
        mode="ema",
        dataframe=dataframe,
        prefix=prefix,
        inplace=inplace,
        **kwargs,
    )


def ma(
    series: pd.Series | str = "close",
    period: int = None,
    mode: Literal[
        "sma", "ema", "wma", "dema", "tema", "trima", "kama", "mama", "t3"
    ] = None,
    dataframe: pd.DataFrame = None,
    prefix: str = "",
    inplace: bool = False,
    **kwargs,
) -> pd.Series | pd.DataFrame:
    """Moving Average

    Args:
        series (pd.Series | str, optional): _description_. Defaults to "close".
        period (int, optional): _description_. Defaults to None.
        mode (Literal[ "sma", "ema", "wma", "dema", "tema", "trima", "kama", "mama", "t3" ], optional): _description_. Defaults to None.
        dataframe (pd.DataFrame, optional): _description_. Defaults to None.
        prefix (str, optional): _description_. Defaults to "".
        inplace (bool, optional): _description_. Defaults to False.

    Raises:
        RuntimeError: _description_

    Returns:
        pd.Series | pd.DataFrame: _description_
    """
    # Validation & init
    if __debug__:
        if period is None or period <= 0:
            raise RuntimeError(f"Period {period} is invalid")
        if mode is None:
            raise RuntimeError(f"Mode {period} is invalid")
    series = series_init(series=series, dataframe=dataframe, inplace=inplace)

    # Indicator
    ma_fn = talib_ma(mode)
    i = ma_fn(series, timeperiod=period, **kwargs)

    if inplace:
        dataframe[f"{prefix}{mode}"] = i
        return dataframe

    return i
