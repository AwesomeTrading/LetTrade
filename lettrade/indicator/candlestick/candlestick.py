import pandas as pd


def cdl_direction(
    dataframe: pd.DataFrame,
    prefix: str = "cdl_",
    inplace: bool = False,
) -> pd.Series | pd.DataFrame:
    """Direction of candle

    Args:
        dataframe (pd.DataFrame): _description_
        prefix (str, optional): _description_. Defaults to "".
        suffix (str, optional): _description_. Defaults to "".
        inplace (bool, optional): _description_. Defaults to False.

    Returns:
        pd.Series | pd.DataFrame: `pd.Series` return [100, 0 , -100]
            - `100` for bull bar
            - `-100` for bear bar
            - `0` for None
    """
    if __debug__:
        if not isinstance(dataframe, pd.DataFrame):
            raise RuntimeError(
                f"dataframe type '{type(dataframe)}' "
                "is not instance of pandas.DataFrame"
            )
    i = dataframe.apply(
        lambda r: 100 if r.open < r.close else -100 if r.open > r.close else 0,
        axis=1,
    ).astype(int)

    if inplace:
        dataframe[f"{prefix}direction"] = i
        return dataframe

    return i