import pandas as pd
import plotly.graph_objects as go

from lettrade.data import DataFeed


def plot_ichimoku(
    df: DataFeed,
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
                x=df.datetime,
                y=df[tenkan_sen],
                name=tenkan_sen,
                type="scatter",
                mode="lines",
                line=dict(color=tenkan_sen_color, width=width),
            ),
            dict(
                x=df.datetime,
                y=df[kijun_sen],
                name=kijun_sen,
                type="scatter",
                mode="lines",
                line=dict(color=kijun_sen_color, width=width),
            ),
            dict(
                x=df.datetime,
                y=df[senkou_span_a],
                name=senkou_span_a,
                type="scatter",
                mode="lines",
                line=dict(color=senkou_span_a_color, width=width),
            ),
            dict(
                x=df.datetime,
                y=df[senkou_span_b],
                name=senkou_span_b,
                type="scatter",
                mode="lines",
                fill="tonexty",
                line=dict(color=senkou_span_b_color, width=width),
            ),
            dict(
                x=df.datetime,
                y=df[chikou_span],
                name=chikou_span,
                type="scatter",
                mode="lines",
                line=dict(color=chikou_span_color, width=width),
            ),
        ]
    )


def plot_line(
    df: DataFeed,
    line: str,
    color: str = "#ffee58",
    width: int = 1,
    **kwargs,
):
    return dict(
        scatters=[
            dict(
                x=df.datetime,
                y=df[line],
                line=dict(color=color, width=width),
                name=line,
                **kwargs,
            )
        ]
    )


def plot_candle_highlight(
    df: DataFeed,
    signal: str,
    name: str = "Candle {df.name}",
    width: int = 1,
    increasing_line_color="#26c6da",
    decreasing_line_color="#ab47bc",
    **kwargs,
):
    plot_df = df.loc[(df[signal] == True)]
    name = name.format(df=df)
    return dict(
        traces=[
            go.Candlestick(
                x=plot_df.index,
                open=plot_df.open,
                high=plot_df.high,
                low=plot_df.low,
                close=plot_df.close,
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
