import pandas as pd
import talib.abstract as ta


def cdl_3blackcrows(dataframe: pd.DataFrame, **kwargs) -> pd.Series | pd.DataFrame:
    return cdl_pattern(dataframe=dataframe, name="3blackcrows", **kwargs)


def cdl_3whitesoldiers(dataframe: pd.DataFrame, **kwargs) -> pd.Series | pd.DataFrame:
    return cdl_pattern(dataframe=dataframe, name="3whitesoldiers", **kwargs)


def cdl_pattern(
    dataframe: pd.DataFrame,
    name: str,
    prefix: str = "cdl_",
    inplace: bool = False,
) -> pd.Series | pd.DataFrame:
    """_summary_

    Args:
        df (pd.DataFrame): _description_
        suffix (str, optional): _description_. Defaults to "".

    Returns:
        pd.Series: _description_
    """
    if __debug__:
        if not isinstance(dataframe, pd.DataFrame):
            raise RuntimeError(
                f"dataframe type '{type(dataframe)}' "
                "is not instance of pandas.DataFrame"
            )

    i = getattr(ta, f"CDL{name.upper()}")(dataframe)

    if inplace:
        dataframe[f"{prefix}{name.lower()}"] = i
        return dataframe

    return i
