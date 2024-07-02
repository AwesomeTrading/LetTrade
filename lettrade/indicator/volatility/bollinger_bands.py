from typing import Literal

import pandas as pd
import talib.abstract as ta

from ..series import series_init
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
    series = series_init(series=series, dataframe=dataframe, inplace=inplace)

    i_upper, i_basis, i_lower = ta.BBANDS(
        series,
        timeperiod=window,
        nbdevup=std,
        nbdevdn=std,
        matype=talib_ma_mode(ma_mode),
    )

    # Result is inplace or new dict
    result = dataframe if inplace else {}
    result[f"{prefix}upper"] = i_upper
    result[f"{prefix}basis"] = i_basis
    result[f"{prefix}lower"] = i_lower
    return result
