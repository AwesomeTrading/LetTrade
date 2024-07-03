import pandas as pd

from .helper import plot_merge


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

    Returns:
        dict: _description_
    """
    return dict(
        items=[
            dict(
                type="scatter",
                x=dataframe.index,
                y=dataframe[tenkan_sen],
                name=tenkan_sen,
                mode="lines",
                line=dict(color=tenkan_sen_color, width=width),
            ),
            dict(
                type="scatter",
                x=dataframe.index,
                y=dataframe[kijun_sen],
                name=kijun_sen,
                mode="lines",
                line=dict(color=kijun_sen_color, width=width),
            ),
            dict(
                type="scatter",
                x=dataframe.index,
                y=dataframe[senkou_span_a],
                name=senkou_span_a,
                mode="lines",
                line=dict(color=senkou_span_a_color, width=width),
            ),
            dict(
                type="scatter",
                x=dataframe.index,
                y=dataframe[senkou_span_b],
                name=senkou_span_b,
                mode="lines",
                fill="tonexty",
                line=dict(color=senkou_span_b_color, width=width),
            ),
            dict(
                type="scatter",
                x=dataframe.index,
                y=dataframe[chikou_span],
                name=chikou_span,
                mode="lines",
                line=dict(color=chikou_span_color, width=width),
            ),
        ]
    )


def plot_line(
    series: pd.Series,
    color: str = "#ffee58",
    width: int = 1,
    name=None,
    mode="lines",
    **kwargs,
) -> dict:
    """_summary_

    Args:
        series (pd.Series): _description_
        color (str, optional): _description_. Defaults to "#ffee58".
        width (int, optional): _description_. Defaults to 1.
        name (_type_, optional): _description_. Defaults to None.
        mode (str, optional): _description_. Defaults to "lines".

    Returns:
        dict: _description_
    """
    return dict(
        items=[
            dict(
                type="scatter",
                x=series.index,
                y=series,
                line=dict(color=color, width=width),
                name=name or series.name,
                mode=mode,
                **kwargs,
            )
        ]
    )


def plot_lines(
    *serieses: list[pd.Series],
    color: str = "#ffee58",
    width: int = 1,
    name=None,
    mode="lines",
    **kwargs,
) -> dict:
    """_summary_

    Args:
        color (str, optional): _description_. Defaults to "#ffee58".
        width (int, optional): _description_. Defaults to 1.
        name (_type_, optional): _description_. Defaults to None.
        mode (str, optional): _description_. Defaults to "lines".

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
                **kwargs,
            ),
        )
    return result


def plot_mark(
    series: pd.Series,
    color: str = "#ffee58",
    width: int = 1,
    mode="markers",
    name=None,
    **kwargs,
) -> dict:
    """_summary_

    Args:
        series (pd.Series): _description_
        color (str, optional): _description_. Defaults to "#ffee58".
        width (int, optional): _description_. Defaults to 1.
        mode (str, optional): _description_. Defaults to "markers".
        name (_type_, optional): _description_. Defaults to None.

    Returns:
        dict: _description_
    """
    return plot_line(
        series=series,
        color=color,
        width=width,
        mode=mode,
        name=name,
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
    **kwargs,
) -> dict:
    """_summary_

    Args:
        dataframe (pd.DataFrame): _description_
        name (str, optional): _description_. Defaults to "Candle highlight".
        width (int, optional): _description_. Defaults to 1.
        increasing_line_color (str, optional): _description_. Defaults to "#26c6da".
        decreasing_line_color (str, optional): _description_. Defaults to "#ab47bc".

    Returns:
        dict: _description_
    """
    return dict(
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
