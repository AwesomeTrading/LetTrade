import plotly.graph_objects as go
from plotly.subplots import make_subplots

from ..data import DataFeed


class Plotter:
    figure: go.Figure = None

    def __init__(self, datas: list[DataFeed]) -> None:
        self.datas: list[DataFeed] = datas
        self.data: DataFeed = datas[0]

    def base(self):
        df = self.datas[0]

        self.figure = go.Figure(
            data=[
                go.Candlestick(
                    # x=df.index,
                    x=df["datetime"],
                    open=df["open"],
                    high=df["high"],
                    low=df["low"],
                    close=df["close"],
                ),
                go.Scatter(
                    # x=df.index,
                    x=df["datetime"],
                    y=df["ema1"],
                    line=dict(color="blue", width=1),
                    name="ema1",
                ),
                go.Scatter(
                    # x=df.index,
                    x=df["datetime"],
                    y=df["ema2"],
                    line=dict(color="green", width=1),
                    name="ema2",
                ),
            ]
        )

    def plot(self):
        if self.figure is None:
            self.base()

        # self.figure.add_scatter(
        #     x=df.index,
        #     y=df["pointpos"],
        #     mode="markers",
        #     marker=dict(size=5, color="MediumPurple"),
        #     name="Signal",
        # )
        self.figure.update_layout()
        self.figure.show()
