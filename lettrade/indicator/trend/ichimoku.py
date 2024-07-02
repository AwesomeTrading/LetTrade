import pandas as pd


def ichimoku(
    dataframe: pd.DataFrame,
    conversion_line_window: int = 9,
    base_line_windows: int = 26,
    laggin_span: int = 52,
    displacement: int = 26,
    cloud: bool = False,
    prefix: str = "",
    inplace: bool = False,
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

    Returns:
        dict[str, pd.Series] | pd.DataFrame: {tenkan_sen, kijun_sen, senkou_span_a, senkou_span_b, leading_senkou_span_a,
        leading_senkou_span_b, chikou_span, cloud_white, cloud_black}
    """
    if __debug__:
        if not isinstance(dataframe, pd.DataFrame):
            raise RuntimeError(
                f"dataframe type '{type(dataframe)}' "
                "is not instance of pandas.DataFrame"
            )

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

    if cloud:
        cloud_white = senkou_span_a > senkou_span_b
        cloud_black = senkou_span_b > senkou_span_a

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
        result[f"{prefix}cloud_white"] = cloud_white
        result[f"{prefix}cloud_black"] = cloud_black

    return result
