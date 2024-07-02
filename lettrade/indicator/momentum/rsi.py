import pandas as pd
import talib.abstract as ta

from ..series import series_init


def rsi(
    series: pd.Series | str = "close",
    window: int = None,
    dataframe: pd.DataFrame = None,
    prefix: str = "",
    inplace: bool = False,
    **kwargs,
) -> pd.Series | pd.DataFrame:
    """_summary_

    Args:
        series (pd.Series | str, optional): _description_. Defaults to "close".
        window (int, optional): _description_. Defaults to None.
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
        if window is None or window <= 0:
            raise RuntimeError(f"Window {window} is invalid")
    series = series_init(series=series, dataframe=dataframe, inplace=inplace)

    # Indicator
    i = ta.RSI(series, timeperiod=window, **kwargs)

    if inplace:
        dataframe[f"{prefix}rsi"] = i
        return dataframe

    return i
