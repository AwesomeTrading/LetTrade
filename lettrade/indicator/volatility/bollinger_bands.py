from typing import Literal

import pandas as pd
import talib.abstract as ta

from ..utils import talib_ma_mode


def bollinger_bands(
    series: pd.Series | str = "close",
    window: int = None,
    std: int | float = None,
    dataframe: pd.DataFrame = None,
    ma_mode: Literal["ema", "sma"] = "sma",
    prefix: str = "bb_",
    inplace: bool = False,
    **kwargs,
) -> dict[str, pd.Series] | pd.DataFrame:

    if __debug__:
        if window is None or window <= 0:
            raise RuntimeError(f"Window {window} is invalid")

        if dataframe is None:
            if not isinstance(series, pd.Series):
                raise RuntimeError(
                    f"series type '{type(series)}' is not instance of pandas.Series"
                )

            if inplace:
                raise RuntimeError("dataframe isnot set when inplace=True")
        else:
            if not isinstance(dataframe, pd.DataFrame):
                raise RuntimeError(
                    f"dataframe type '{type(dataframe)}' "
                    "is not instance of pandas.DataFrame"
                )

            if not isinstance(series, str):
                raise RuntimeError(
                    f"Series type {type(series)} is not string of column name"
                )

            series = dataframe[series]

    i_upper, i_basis, i_lower = ta.BBANDS(
        series,
        window,
        std,
        std,
        talib_ma_mode(ma_mode),
    )

    # Result is inplace or new dict
    result = dataframe if inplace else {}
    result[f"{prefix}upper"] = i_upper
    result[f"{prefix}basis"] = i_basis
    result[f"{prefix}lower"] = i_lower
    return result
