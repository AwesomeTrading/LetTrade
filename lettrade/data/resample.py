import pandas as pd


def resample(df: pd.DataFrame, timeframe: str = "5min") -> pd.DataFrame:
    ohlc_dict = {
        "open": "first",
        "high": "max",
        "low": "min",
        "close": "last",
        "volume": "sum",
    }
    # Resample to "left" border as dates are candle open dates
    df = df.resample(timeframe, label="left").agg(ohlc_dict).dropna()
    return df
