import pandas as pd
import talib.abstract as ta


def cdl_3blackcrows(df: pd.DataFrame, suffix: str = "") -> pd.Series:
    """_summary_

    Args:
        df (pd.DataFrame): _description_
        suffix (str, optional): _description_. Defaults to "".

    Returns:
        pd.Series: _description_
    """
    i = ta.CDL3BLACKCROWS(df)
    i.name = f"3blackcrows{suffix}"
    return i


def cdl_3whitesoldiers(df: pd.DataFrame, suffix: str = "") -> pd.Series:
    """_summary_

    Args:
        df (pd.DataFrame): _description_
        suffix (str, optional): _description_. Defaults to "".

    Returns:
        pd.Series: _description_
    """
    i = ta.CDL3WHITESOLDIERS(df)
    i.name = f"3whitesoldiers{suffix}"
    return i
