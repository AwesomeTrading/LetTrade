import pandas as pd
import talib.abstract as ta


def cdl_3blackcrows(df: pd.DataFrame, suffix: str = "") -> pd.Series:
    i = ta.CDL3BLACKCROWS(df)
    suffix = f"_{suffix}" if suffix else ""
    i.name = f"3blackcrows{suffix}"
    return i


def cdl_3whitesoldiers(df: pd.DataFrame, suffix: str = "") -> pd.Series:
    i = ta.CDL3WHITESOLDIERS(df)
    suffix = f"_{suffix}" if suffix else ""
    i.name = f"3whitesoldiers{suffix}"
    return i
