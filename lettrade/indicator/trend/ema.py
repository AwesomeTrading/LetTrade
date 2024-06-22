import pandas as pd
import talib.abstract as ta


def ema(
    dataframe: pd.DataFrame,
    period: int,
    prefix: str = "cdl_",
    inplace: bool = False,
    **kwargs,
) -> pd.Series | pd.DataFrame:
    """Exponential Moving Average

    Args:
        dataframe (pd.DataFrame): _description_
        prefix (str, optional): _description_. Defaults to "cdl_".
        inplace (bool, optional): _description_. Defaults to False.

    Raises:
        RuntimeError: _description_

    Returns:
        pd.Series | pd.DataFrame: _description_
    """
    if __debug__:
        if not isinstance(dataframe, pd.DataFrame):
            raise RuntimeError(
                f"dataframe type '{type(dataframe)}' "
                "is not instance of pandas.DataFrame"
            )

    i = ta.EMA(dataframe, timeperiod=period, **kwargs)

    if inplace:
        dataframe[f"{prefix}ema"] = i
        return dataframe

    return i
