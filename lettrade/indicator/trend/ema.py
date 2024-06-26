import pandas as pd
import talib.abstract as ta


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
    if __debug__:
        if period is None or period <= 0:
            raise RuntimeError(f"Period {period} is invalid")

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

    i = ta.EMA(series, timeperiod=period, **kwargs)

    if inplace:
        dataframe[f"{prefix}ema"] = i
        return dataframe

    return i
