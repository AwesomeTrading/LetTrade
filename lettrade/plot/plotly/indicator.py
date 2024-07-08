import pandas as pd

from lettrade.plot.helper import plot_merge


def plot_ichimoku(
    dataframe: pd.DataFrame,
    tenkan_sen="tenkan_sen",
    kijun_sen="kijun_sen",
    senkou_span_a="senkou_span_a",
    senkou_span_b="senkou_span_b",
    chikou_span="chikou_span",
    width=1,
    tenkan_sen_color="#33BDFF",
    kijun_sen_color="#D105F5",
    senkou_span_a_color="#228B22",
    senkou_span_b_color="#FF3342",
    chikou_span_color="#F1F316",
    filter: pd.Series | None = None,
) -> dict:
    """_summary_

    Args:
        dataframe (pd.DataFrame): _description_
        tenkan_sen (str, optional): _description_. Defaults to "tenkan_sen".
        kijun_sen (str, optional): _description_. Defaults to "kijun_sen".
        senkou_span_a (str, optional): _description_. Defaults to "senkou_span_a".
        senkou_span_b (str, optional): _description_. Defaults to "senkou_span_b".
        chikou_span (str, optional): _description_. Defaults to "chikou_span".
        width (int, optional): _description_. Defaults to 1.
        tenkan_sen_color (str, optional): _description_. Defaults to "#33BDFF".
        kijun_sen_color (str, optional): _description_. Defaults to "#D105F5".
        senkou_span_a_color (str, optional): _description_. Defaults to "#228B22".
        senkou_span_b_color (str, optional): _description_. Defaults to "#FF3342".
        chikou_span_color (str, optional): _description_. Defaults to "#F1F316".
        filter (pd.Series | None, optional): _description_. Defaults to None.

    Returns:
        dict: _description_
    """
    if filter is not None:
        df_name = dataframe.name
        dataframe = dataframe.loc[filter]
        object.__setattr__(dataframe, "name", df_name)

    items = []

    if tenkan_sen is not None:
        items.append(
            dict(
                type="scatter",
                x=dataframe.index,
                y=dataframe[tenkan_sen],
                name=tenkan_sen,
                mode="lines",
                line=dict(color=tenkan_sen_color, width=width),
            )
        )
    if kijun_sen is not None:
        items.append(
            dict(
                type="scatter",
                x=dataframe.index,
                y=dataframe[kijun_sen],
                name=kijun_sen,
                mode="lines",
                line=dict(color=kijun_sen_color, width=width),
            )
        )
    if senkou_span_a is not None:
        items.append(
            dict(
                type="scatter",
                x=dataframe.index,
                y=dataframe[senkou_span_a],
                name=senkou_span_a,
                mode="lines",
                line=dict(color=senkou_span_a_color, width=width),
            )
        )
    if senkou_span_b is not None:
        items.append(
            dict(
                type="scatter",
                x=dataframe.index,
                y=dataframe[senkou_span_b],
                name=senkou_span_b,
                mode="lines",
                fill="tonexty",
                line=dict(color=senkou_span_b_color, width=width),
            )
        )
    if chikou_span is not None:
        items.append(
            dict(
                type="scatter",
                x=dataframe.index,
                y=dataframe[chikou_span],
                name=chikou_span,
                mode="lines",
                line=dict(color=chikou_span_color, width=width),
            )
        )

    return {f"{dataframe.name}": dict(items=items)}


def plot_bollinger_bands(
    dataframe: pd.DataFrame,
    upper: str | None = "upper",
    basis: str | None = "basis",
    lower: str | None = "lower",
    width: int = 1,
    upper_color: str = "#33BDFF",
    basis_color: str = "#D105F5",
    lower_color: str = "#33BDFF",
    filter: pd.Series | None = None,
) -> dict:
    """_summary_

    Args:
        dataframe (pd.DataFrame): _description_
        upper (str, optional): Column name. `None` mean skip plot. Defaults to "upper".
        basis (str, optional): Column name. `None` mean skip plot. Defaults to "basis".
        lower (str, optional): Column name. `None` mean skip plot. Defaults to "lower".
        width (int, optional): _description_. Defaults to 1.
        upper_color (str, optional): Color code. Defaults to "#33BDFF".
        lower_color (str, optional): Color code. Defaults to "#33BDFF".
        basis_color (str, optional): Color code. Defaults to "#D105F5".
        filter (pd.Series | None, optional): _description_. Defaults to None.

    Returns:
        dict: _description_
    """
    if filter is not None:
        df_name = dataframe.name
        dataframe = dataframe.loc[filter]
        object.__setattr__(dataframe, "name", df_name)

    items = []

    if upper is not None:
        items.append(
            dict(
                type="scatter",
                x=dataframe.index,
                y=dataframe[upper],
                name=upper,
                mode="lines",
                line=dict(color=upper_color, width=width),
            )
        )
    if basis is not None:
        items.append(
            dict(
                type="scatter",
                x=dataframe.index,
                y=dataframe[basis],
                name=basis,
                mode="lines",
                line=dict(color=basis_color, width=width),
            )
        )
    if lower is not None:
        items.append(
            dict(
                type="scatter",
                x=dataframe.index,
                y=dataframe[lower],
                name=lower,
                mode="lines",
                line=dict(color=lower_color, width=width),
            )
        )
    return {f"{dataframe.name}": dict(items=items)}


plot_keltner_channel = plot_bollinger_bands


def plot_parabolic_sar(
    dataframe: pd.DataFrame,
    long: str | None = "long",
    short: str | None = "short",
    width: int = 1,
    long_color: str = "#33BDFF",
    short_color: str = "#D105F5",
    filter: pd.Series | None = None,
) -> dict:
    """_summary_

    Args:
        dataframe (pd.DataFrame): _description_
        long (str | None, optional): _description_. Defaults to "long".
        short (str | None, optional): _description_. Defaults to "short".
        width (int, optional): _description_. Defaults to 1.
        long_color (str, optional): _description_. Defaults to "#33BDFF".
        short_color (str, optional): _description_. Defaults to "#D105F5".
        filter (pd.Series | None, optional): _description_. Defaults to None.

    Returns:
        dict: _description_
    """
    if filter is not None:
        df_name = dataframe.name
        dataframe = dataframe.loc[filter]
        object.__setattr__(dataframe, "name", df_name)

    config = dict()

    if long is not None:
        plot_merge(
            config,
            plot_mark(
                series=long,
                color=long_color,
                name="psar_long",
                width=width,
                dataframe=dataframe,
            ),
        )
    if short is not None:
        plot_merge(
            config,
            plot_mark(
                series=short,
                color=short_color,
                name="psar_short",
                width=width,
                dataframe=dataframe,
            ),
        )
    return config


def plot_line(
    series: pd.Series | str,
    color: str = "#ffee58",
    width: int = 1,
    name: str | None = None,
    mode: str = "lines",
    fullfill: bool = False,
    dataframe: pd.DataFrame | None = None,
    filter: pd.Series | None = None,
    **kwargs,
) -> dict:
    """_summary_

    Args:
        series (pd.Series | str): _description_
        color (str, optional): _description_. Defaults to "#ffee58".
        width (int, optional): _description_. Defaults to 1.
        name (str | None, optional): _description_. Defaults to None.
        mode (str, optional): _description_. Defaults to "lines".
        fullfill (bool, optional): _description_. Defaults to False.
        dataframe (pd.DataFrame | None, optional): _description_. Defaults to None.
        filter (pd.Series | None, optional): _description_. Defaults to None.

    Returns:
        dict: _description_
    """
    if isinstance(series, str):
        series = dataframe[series]

    if filter is not None:
        series = series.loc[filter]

    config = dict(
        items=[
            dict(
                type="scatter",
                x=series.index,
                y=series,
                line=dict(color=color, width=width),
                name=name or series.name,
                mode=mode,
                fullfill=fullfill,
                **kwargs,
            )
        ]
    )
    if dataframe is None:
        return config

    return {f"{dataframe.name}": config}


def plot_lines(
    *serieses: list[pd.Series | str],
    color: str = "#ffee58",
    width: int = 1,
    name: str | None = None,
    mode: str = "lines",
    fullfill: bool = False,
    dataframe: pd.DataFrame | None = None,
    **kwargs,
) -> dict:
    """_summary_

    Args:
        color (str, optional): _description_. Defaults to "#ffee58".
        width (int, optional): _description_. Defaults to 1.
        name (str | None, optional): _description_. Defaults to None.
        mode (str, optional): _description_. Defaults to "lines".
        fullfill (bool, optional): _description_. Defaults to False.
        dataframe (pd.DataFrame | None, optional): _description_. Defaults to None.

    Returns:
        dict: _description_
    """
    result = {}
    for series in serieses:
        plot_merge(
            result,
            plot_line(
                series=series,
                color=color,
                width=width,
                name=name,
                mode=mode,
                fullfill=fullfill,
                dataframe=dataframe,
                **kwargs,
            ),
        )
    return result


def plot_mark(
    series: pd.Series | str,
    color: str = "#ffee58",
    width: int = 1,
    mode: str = "markers",
    name: str | None = None,
    fullfill: bool = False,
    dataframe: pd.DataFrame | None = None,
    filter: pd.Series | None = None,
    **kwargs,
) -> dict:
    """_summary_

    Args:
        series (pd.Series | str): _description_
        color (str, optional): _description_. Defaults to "#ffee58".
        width (int, optional): _description_. Defaults to 1.
        mode (str, optional): _description_. Defaults to "markers".
        name (str | None, optional): _description_. Defaults to None.
        fullfill (bool, optional): _description_. Defaults to False.
        dataframe (pd.DataFrame | None, optional): _description_. Defaults to None.
        filter (pd.Series | None, optional): _description_. Defaults to None.

    Returns:
        dict: _description_
    """

    return plot_line(
        series=series,
        color=color,
        width=width,
        mode=mode,
        name=name,
        fullfill=fullfill,
        dataframe=dataframe,
        filter=filter,
        **kwargs,
    )


def plot_candlestick(
    dataframe: pd.DataFrame,
    name: str = "Candlestick",
    width: int = 1,
    increasing_line_color="#26c6da",
    decreasing_line_color="#ab47bc",
    row: int = 1,
    col: int = 1,
    filter: pd.Series | None = None,
    **kwargs,
) -> dict:
    """_summary_

    Args:
        dataframe (pd.DataFrame): _description_
        name (str, optional): _description_. Defaults to "Candlestick".
        width (int, optional): _description_. Defaults to 1.
        increasing_line_color (str, optional): _description_. Defaults to "#26c6da".
        decreasing_line_color (str, optional): _description_. Defaults to "#ab47bc".
        row (int, optional): _description_. Defaults to 1.
        col (int, optional): _description_. Defaults to 1.
        filter (pd.Series | None, optional): _description_. Defaults to None.

    Returns:
        dict: _description_
    """
    if filter is not None:
        df_name = dataframe.name
        dataframe = dataframe.loc[filter]
        object.__setattr__(dataframe, "name", df_name)

    config = dict(
        items=[
            dict(
                type="candlestick",
                x=dataframe.index,
                open=dataframe["open"],
                high=dataframe["high"],
                low=dataframe["low"],
                close=dataframe["close"],
                name=name,
                line=dict(width=width),
                increasing_line_color=increasing_line_color,
                decreasing_line_color=decreasing_line_color,
                hoverinfo="text",
                hovertext=name,
                row=row,
                col=col,
                **kwargs,
            ),
        ]
    )

    return {f"{dataframe.name}": config}
