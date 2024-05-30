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


def plot_line(df: DataFeed, line: str, color: str = "blue", width: int = 1):
    return dict(
        scatters=[
            dict(
                x=df.datetime,
                y=df[line],
                line=dict(color=color, width=width),
                name=line,
            )
        ]
    )
