import pandas as pd


def cdl_direction(df: pd.DataFrame, suffix: str = "") -> pd.Series:
    """Direction of candle

    Args:
        df (pd.DataFrame): _description_
        suffix (str, optional): _description_. Defaults to "".

    Returns:
        pd.Series: [100, 0 , -100]
            - `100` for bull bar
            - `-100` for bear bar
            - `0` for None
    """
    i = df.apply(
        lambda r: 100 if r.open < r.close else -100 if r.open > r.close else 0,
        axis=1,
    ).astype(int)
    # i = pd.Series(0, index=df.index, name=f"cdl_direction{suffix}")
    # i.loc[(df.open < df.close)] = 100
    # i.loc[(df.open > df.close)] = -100
    i.name = f"cdl_direction{suffix}"
    return i
