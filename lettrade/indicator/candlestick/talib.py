from typing import Literal

import pandas as pd
import talib.abstract as ta


def cdl_pattern(
    dataframe: pd.DataFrame,
    pattern: str,
    name: str | None = None,
    prefix: str = "cdl_",
    inplace: bool = False,
    plot: bool | list = False,
    plot_type: Literal["candlestick", "mark"] = "candlestick",
    plot_kwargs: dict | None = None,
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
        column = name or f"{prefix}{pattern.lower()}"
        dataframe[column] = i

        # Plot
        if plot:
            if plot_kwargs is None:
                plot_kwargs = dict()

            plot_kwargs.update(name=column)

            from lettrade.indicator.plot import indicator_add_plotter
            from lettrade.plot.plotly import plot_candlestick, plot_mark

            filter = i > 0
            if plot_type == "mark":
                plot_kwargs.update(series=i)
                indicator_add_plotter(
                    dataframe=dataframe,
                    plotter=plot_mark,
                    filter=filter,
                    **plot_kwargs,
                )
            else:
                indicator_add_plotter(
                    dataframe=dataframe,
                    plotter=plot_candlestick,
                    filter=filter,
                    **plot_kwargs,
                )

        return dataframe

    return i


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


def cdl_eveningstar(
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
        pattern="eveningstar",
        name=name,
        prefix=prefix,
        inplace=inplace,
        **kwargs,
    )


def cdl_morningstar(
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
        pattern="morningstar",
        name=name,
        prefix=prefix,
        inplace=inplace,
        **kwargs,
    )


def cdl_doji(
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
        pattern="doji",
        name=name,
        prefix=prefix,
        inplace=inplace,
        **kwargs,
    )


def cdl_3inside(
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
        pattern="3inside",
        name=name,
        prefix=prefix,
        inplace=inplace,
        **kwargs,
    )
