import pandas as pd
import plotly.graph_objects as go


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
):
    return dict(
        scatters=[
            dict(
                x=dataframe.index,
                y=dataframe[tenkan_sen],
                name=tenkan_sen,
                type="scatter",
                mode="lines",
                line=dict(color=tenkan_sen_color, width=width),
            ),
            dict(
                x=dataframe.index,
                y=dataframe[kijun_sen],
                name=kijun_sen,
                type="scatter",
                mode="lines",
                line=dict(color=kijun_sen_color, width=width),
            ),
            dict(
                x=dataframe.index,
                y=dataframe[senkou_span_a],
                name=senkou_span_a,
                type="scatter",
                mode="lines",
                line=dict(color=senkou_span_a_color, width=width),
            ),
            dict(
                x=dataframe.index,
                y=dataframe[senkou_span_b],
                name=senkou_span_b,
                type="scatter",
                mode="lines",
                fill="tonexty",
                line=dict(color=senkou_span_b_color, width=width),
            ),
            dict(
                x=dataframe.index,
                y=dataframe[chikou_span],
                name=chikou_span,
                type="scatter",
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
):
    return dict(
        scatters=[
            dict(
                x=series.index,
                y=series,
                line=dict(color=color, width=width),
                name=name or series.name,
                mode=mode,
                **kwargs,
            )
        ]
    )


def plot_mark(
    series: pd.Series,
    color: str = "#ffee58",
    width: int = 1,
    mode="markers",
    name=None,
    **kwargs,
):
    return plot_line(
        series=series,
        color=color,
        width=width,
        mode=mode,
        name=name,
        **kwargs,
    )


def plot_candle_highlight(
    dataframe: pd.DataFrame,
    name: str = "Candle highlight",
    width: int = 1,
    increasing_line_color="#26c6da",
    decreasing_line_color="#ab47bc",
    **kwargs,
):
    return dict(
        traces=[
            go.Candlestick(
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
                **kwargs,
            ),
        ]
    )
