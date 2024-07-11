import pandas as pd
import talib.abstract as ta


def atr(
    dataframe: pd.DataFrame,
    window: int = 20,
    name: str | None = None,
    prefix: str = "",
    inplace: bool = False,
    plot: bool | list[str] = False,
    plot_kwargs: dict | None = None,
) -> dict[str, pd.Series] | pd.DataFrame:
    """_summary_

    Args:
        dataframe (pd.DataFrame): _description_
        window (int, optional): _description_. Defaults to 20.
        name (str | None, optional): _description_. Defaults to None.
        prefix (str, optional): _description_. Defaults to "".
        inplace (bool, optional): _description_. Defaults to False.
        plot (bool | list, optional): _description_. Defaults to False.
        plot_kwargs (dict | None, optional): _description_. Defaults to None.

    Raises:
        RuntimeError: _description_

    Returns:
        dict[str, pd.Series] | pd.DataFrame: {atr}
    """
    if __debug__:
        if not isinstance(dataframe, pd.DataFrame):
            raise RuntimeError(
                f"dataframe type '{type(dataframe)}' "
                "is not instance of pandas.DataFrame"
            )
        if plot and not inplace:
            raise RuntimeError("Cannot plot when inplace=False")

    i = ta.ATR(dataframe, timeperiod=window)

    if inplace:
        name = name or f"{prefix}atr"
        dataframe[name] = i

        # Plot
        if plot:
            if plot_kwargs is None:
                plot_kwargs = dict()

            plot_kwargs.update(series=name, name=name)
            plot_kwargs.setdefault("row", 2)
            plot_kwargs.setdefault("row_height", 0.5)

            from lettrade.indicator.plot import IndicatorPlotter
            from lettrade.plot.plotly import plot_line

            IndicatorPlotter(dataframe=dataframe, plotter=plot_line, **plot_kwargs)

        return dataframe

    return i
