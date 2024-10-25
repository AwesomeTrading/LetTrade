import pandas as pd


def ichimoku(
    dataframe: pd.DataFrame,
    conversion_line_window: int = 9,
    base_line_windows: int = 26,
    laggin_span: int = 52,
    displacement: int = 26,
    cloud: bool = False,
    prefix: str = "ichimoku_",
    inplace: bool = False,
    plot: bool | list[str] = False,
    plot_kwargs: dict | None = None,
) -> dict[str, pd.Series] | pd.DataFrame:
    """Ichimoku cloud indicator

    Note:
        Do not use `chikou_span` for backtesting.
        It looks into the future, is not printed by most charting platforms.
        It is only useful for visual analysis

    Args:
        dataframe (pd.DataFrame): Dataframe containing OHLCV data
        conversion_line_window (int, optional): Conversion line Window. Defaults to 9.
        base_line_windows (int, optional): Base line Windows. Defaults to 26.
        laggin_span (int, optional): Lagging span window. Defaults to 52.
        displacement (int, optional): Displacement (shift). Defaults to 26.
        cloud (bool, optional): Add cloud direction. Defaults to False.
        prefix (str, optional): _description_. Defaults to "ichimoku_".
        inplace (bool, optional): _description_. Defaults to False.
        plot (bool | list, optional): _description_. Defaults to False.
        plot_kwargs (dict | None, optional): _description_. Defaults to None.

    Returns:
        dict[str, pd.Series] | pd.DataFrame: {tenkan_sen, kijun_sen, senkou_span_a, senkou_span_b, leading_senkou_span_a, leading_senkou_span_b, chikou_span, cloud_white, cloud_black}
    """
    if __debug__:
        if not isinstance(dataframe, pd.DataFrame):
            raise RuntimeError(
                f"dataframe type '{type(dataframe)}' "
                "is not instance of pandas.DataFrame"
            )
        if plot and not inplace:
            raise RuntimeError("Cannot plot when inplace=False")

    tenkan_sen = (
        dataframe["high"].rolling(window=conversion_line_window).max()
        + dataframe["low"].rolling(window=conversion_line_window).min()
    ) / 2

    kijun_sen = (
        dataframe["high"].rolling(window=base_line_windows).max()
        + dataframe["low"].rolling(window=base_line_windows).min()
    ) / 2

    leading_senkou_span_a = (tenkan_sen + kijun_sen) / 2

    leading_senkou_span_b = (
        dataframe["high"].rolling(window=laggin_span).max()
        + dataframe["low"].rolling(window=laggin_span).min()
    ) / 2

    senkou_span_a = leading_senkou_span_a.shift(displacement - 1)

    senkou_span_b = leading_senkou_span_b.shift(displacement - 1)

    chikou_span = dataframe["close"].shift(-displacement + 1)

    # Result is inplace or new dict
    result = dataframe if inplace else {}

    result[f"{prefix}tenkan_sen"] = tenkan_sen
    result[f"{prefix}kijun_sen"] = kijun_sen
    result[f"{prefix}senkou_span_a"] = senkou_span_a
    result[f"{prefix}senkou_span_b"] = senkou_span_b
    result[f"{prefix}leading_senkou_span_a"] = leading_senkou_span_a
    result[f"{prefix}leading_senkou_span_b"] = leading_senkou_span_b
    result[f"{prefix}chikou_span"] = chikou_span

    if cloud:
        cloud_white = senkou_span_a > senkou_span_b
        cloud_black = senkou_span_b > senkou_span_a
        result[f"{prefix}cloud_white"] = cloud_white
        result[f"{prefix}cloud_black"] = cloud_black

    if plot:
        if plot_kwargs is None:
            plot_kwargs = dict()

        if isinstance(plot, list):
            if f"{prefix}tenkan_sen" in plot:
                plot_kwargs.update(tenkan_sen=f"{prefix}tenkan_sen")
            if f"{prefix}kijun_sen" in plot:
                plot_kwargs.update(kijun_sen=f"{prefix}kijun_sen")
            if f"{prefix}senkou_span_a" in plot:
                plot_kwargs.update(senkou_span_a=f"{prefix}senkou_span_a")
            if f"{prefix}senkou_span_b" in plot:
                plot_kwargs.update(senkou_span_b=f"{prefix}senkou_span_b")
            if f"{prefix}chikou_span" in plot:
                plot_kwargs.update(chikou_span=f"{prefix}chikou_span")
        else:
            plot_kwargs.update(
                tenkan_sen=f"{prefix}tenkan_sen",
                kijun_sen=f"{prefix}kijun_sen",
                senkou_span_a=f"{prefix}senkou_span_a",
                senkou_span_b=f"{prefix}senkou_span_b",
                chikou_span=f"{prefix}chikou_span",
            )
        from lettrade.indicator.plot import IndicatorPlotter
        from lettrade.plot.plotly import plot_ichimoku

        IndicatorPlotter(dataframe=dataframe, plotter=plot_ichimoku, **plot_kwargs)
    return result
