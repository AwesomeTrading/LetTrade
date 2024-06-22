import pandas as pd


def pandas_inject():
    from pandas.core.base import PandasObject

    PandasObject.signal_direction = signal_direction


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
    if __debug__:
        if not isinstance(dataframe, pd.DataFrame):
            raise RuntimeError(
                f"dataframe type '{type(dataframe)}' "
                "is not instance of pandas.DataFrame"
            )

    s = pd.Series(value, index=dataframe.index, name=name, **kwargs)
    s.loc[signal_up] = value_up
    s.loc[signal_down] = value_down

    if inplace:
        dataframe[name] = s
        return dataframe

    return s
