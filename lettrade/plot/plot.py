import plotly.graph_objects as go
from plotly.subplots import make_subplots

from ..data import DataFeed


class Plotting:
    def __init__(self, datas: list[DataFeed]) -> None:
        self.datas: list[DataFeed] = datas
        self.data: DataFeed = datas[0]

    def plot(self):
        df = self.datas[0]

        fig = go.Figure(
            data=[
                go.Candlestick(
                    x=df.index,
                    open=df["open"],
                    high=df["high"],
                    low=df["low"],
                    close=df["close"],
                ),
                go.Scatter(
                    x=df.index,
                    y=df["ema1"],
                    line=dict(color="blue", width=1),
                    name="ema1",
                ),
                go.Scatter(
                    x=df.index,
                    y=df["ema2"],
                    line=dict(color="green", width=1),
                    name="ema2",
                ),
            ]
        )

        # fig.add_scatter(
        #     x=df.index,
        #     y=df["pointpos"],
        #     mode="markers",
        #     marker=dict(size=5, color="MediumPurple"),
        #     name="Signal",
        # )
        fig.update_layout()
        fig.show()
