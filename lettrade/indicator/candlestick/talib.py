import pandas as pd
import talib.abstract as ta


def cdl_3blackcrows(
    dataframe: pd.DataFrame,
    name: str | None = None,
    prefix: str = "cdl_",
    inplace: bool = False,
    **kwargs,
) -> pd.Series | pd.DataFrame:
    """_summary_

    Args:
        dataframe (pd.DataFrame): _description_
        name (str | None, optional): _description_. Defaults to None.
        prefix (str, optional): _description_. Defaults to "cdl_".
        inplace (bool, optional): _description_. Defaults to False.

    Returns:
        pd.Series | pd.DataFrame: _description_
    """
    return cdl_pattern(
        dataframe=dataframe,
        pattern="3blackcrows",
        name=name,
        prefix=prefix,
        inplace=inplace,
        **kwargs,
    )


def cdl_3whitesoldiers(
    dataframe: pd.DataFrame,
    name: str | None = None,
    prefix: str = "cdl_",
    inplace: bool = False,
    **kwargs,
) -> pd.Series | pd.DataFrame:
    """_summary_

    Args:
        dataframe (pd.DataFrame): _description_
        name (str | None, optional): _description_. Defaults to None.
        prefix (str, optional): _description_. Defaults to "cdl_".
        inplace (bool, optional): _description_. Defaults to False.

    Returns:
        pd.Series | pd.DataFrame: _description_
    """
    return cdl_pattern(
        dataframe=dataframe,
        pattern="3whitesoldiers",
        name=name,
        prefix=prefix,
        inplace=inplace,
        **kwargs,
    )


def cdl_pattern(
    dataframe: pd.DataFrame,
    pattern: str,
    name: str | None = None,
    prefix: str = "cdl_",
    inplace: bool = False,
    **kwargs,
) -> pd.Series | pd.DataFrame:
    """_summary_

    Args:
        dataframe (pd.DataFrame): pandas.DataFrame with ohlcv
        pattern (str): TA-Lib candle pattern name. Ex: `3whitesoldiers`, `3blackcrows`
        name (str | None, optional): _description_. Defaults to None.
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
        dataframe[name or f"{prefix}{pattern.lower()}"] = i
        return dataframe

    return i
