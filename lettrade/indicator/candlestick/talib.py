import pandas as pd
import talib.abstract as ta


def cdl_3blackcrows(
    dataframe: pd.DataFrame,
    prefix: str = "cdl_",
    inplace: bool = False,
    **kwargs,
) -> pd.Series | pd.DataFrame:
    """_summary_

    Args:
        dataframe (pd.DataFrame): _description_
        prefix (str, optional): _description_. Defaults to "cdl_".
        inplace (bool, optional): _description_. Defaults to False.

    Returns:
        pd.Series | pd.DataFrame: _description_
    """
    return cdl_pattern(
        dataframe=dataframe,
        pattern="3blackcrows",
        prefix=prefix,
        inplace=inplace,
        **kwargs,
    )


def cdl_3whitesoldiers(
    dataframe: pd.DataFrame,
    prefix: str = "cdl_",
    inplace: bool = False,
    **kwargs,
) -> pd.Series | pd.DataFrame:
    """_summary_

    Args:
        dataframe (pd.DataFrame): _description_
        prefix (str, optional): _description_. Defaults to "cdl_".
        inplace (bool, optional): _description_. Defaults to False.

    Returns:
        pd.Series | pd.DataFrame: _description_
    """
    return cdl_pattern(
        dataframe=dataframe,
        pattern="3whitesoldiers",
        prefix=prefix,
        inplace=inplace,
        **kwargs,
    )


def cdl_pattern(
    dataframe: pd.DataFrame,
    pattern: str,
    prefix: str = "cdl_",
    inplace: bool = False,
    **kwargs,
) -> pd.Series | pd.DataFrame:
    """_summary_

    Args:
        dataframe (pd.DataFrame): pandas.DataFrame with ohlcv
        pattern (str): TA-Lib candle pattern name.
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

    i = getattr(ta, f"CDL{pattern.upper()}")(dataframe, **kwargs)

    if inplace:
        dataframe[f"{prefix}{pattern.lower()}"] = i
        return dataframe

    return i
