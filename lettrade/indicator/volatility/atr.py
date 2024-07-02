import pandas as pd
import talib.abstract as ta


def atr(
    dataframe: pd.DataFrame,
    window: int = 20,
    prefix: str = "",
    inplace: bool = False,
) -> dict[str, pd.Series] | pd.DataFrame:
    """_summary_

    Args:
        dataframe (pd.DataFrame): _description_
        window (int, optional): _description_. Defaults to 20.
        prefix (str, optional): _description_. Defaults to "".
        inplace (bool, optional): _description_. Defaults to False.

    Raises:
        RuntimeError: _description_

    Returns:
        dict[str, pd.Series] | pd.DataFrame: _description_
    """
    if __debug__:
        if not isinstance(dataframe, pd.DataFrame):
            raise RuntimeError(
                f"dataframe type '{type(dataframe)}' "
                "is not instance of pandas.DataFrame"
            )

    i = ta.ATR(dataframe, timeperiod=window)

    if inplace:
        dataframe[f"{prefix}atr"] = i
        return dataframe

    return i
