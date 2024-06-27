from typing import Any

import pandas as pd


def pandas_inject(obj: object | None = None):
    if obj is None:
        from pandas.core.base import PandasObject

        obj = PandasObject

    obj.signal_direction = signal_direction
    obj.signal_condiction = signal_condiction


def signal_direction(
    dataframe: pd.DataFrame,
    signal_up: pd.Series,
    signal_down: pd.Series,
    name: str,
    value: int = 0,
    value_up: int = 100,
    value_down: int = -100,
    inplace: bool = False,
    **kwargs,
) -> pd.Series | pd.DataFrame:
    """Define a signal with 2 direction Up and Down

    Args:
        dataframe (pd.DataFrame): _description_
        signal_up (pd.Series): _description_
        signal_down (pd.Series): _description_
        name (str): Name of signal, column name when add to DataFrame with inplace=True.
        value (int, optional): Default value when condiction is not matched. Defaults to 0.
        value_up (int, optional): _description_. Defaults to 100.
        value_down (int, optional): _description_. Defaults to -100.
        inplace (bool, optional): Whether to add to the DataFrame and return DataFrame rather than return result. Defaults to False.

    Returns:
        pd.Series | pd.DataFrame: _description_
    """
    return signal_condiction(
        dataframe,
        [signal_up, value_up],
        [signal_down, value_down],
        name=name,
        value=value,
        inplace=inplace,
        **kwargs,
    )


def signal_condiction(
    dataframe: pd.DataFrame,
    *condictions: list[list[pd.Series | Any]],
    name: str,
    value: int | float = 0,
    inplace: bool = False,
    **kwargs,
) -> pd.Series | pd.DataFrame:
    """Define a signal with multiple condiction

    Args:
        dataframe (pd.DataFrame): _description_
        *condictions (list[list[pd.Series | Any]]): Pairs of condiction [`<pandas.Series condiction>`, `<value>`]
        name (str): Name of signal, column name when add to DataFrame with inplace=True.
        value (int, optional): Default value when condiction is not matched. Defaults to 0.
        inplace (bool, optional): _description_. Defaults to False.

    Usage:
        ```python
        df.i.signal_condiction(
            [df["close"] > df["open"], 100],
            [df["close"] < df["open"], -100],
            name="cdl_direction",
            inplace=True,
        )
        ```

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

    s = pd.Series(value, index=dataframe.index, name=name, **kwargs)
    for condiction in condictions:
        s.loc[condiction[0]] = condiction[1]

    if inplace:
        dataframe[name] = s
        return dataframe

    return s
