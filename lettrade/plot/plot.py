from typing import Mapping

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from ..base import BaseDataFeeds
from ..data import DataFeed, DataFeeder


class Plotter(BaseDataFeeds):
    figure: go.Figure = None

    _stored_datas: dict = {}

    def __init__(self, feeder: DataFeeder) -> None:
        self.feeder: DataFeeder = feeder

    def load(self):
        df = self.data

        self.figure: go.Figure = go.Figure(
            data=[
                go.Candlestick(
                    x=df.index,
                    open=df["open"],
                    high=df["high"],
                    low=df["low"],
                    close=df["close"],
                    name="Price",
                    hoverinfo="x+y",
                    customdata=df["datetime"],
                ),
                go.Scatter(
                    x=df.index,
                    meta=df["datetime"],
                    y=df["ema1"],
                    line=dict(color="blue", width=1),
                    name="ema1",
                ),
                go.Scatter(
                    x=df.index,
                    meta=df["datetime"],
                    y=df["ema2"],
                    line=dict(color="green", width=1),
                    name="ema2",
                ),
            ]
        )
        self.figure.update_layout(hovermode="x unified")

    def jump(self, index, range=300, data=None):
        if data is None:
            data = self.data

        name = data.info["name"]

        stored_data: DataFeed = self._stored_datas.setdefault(name, data)
        self.data = DataFeed(name=name, data=stored_data[index : index + range].copy())

        self.load()

    def plot(self, *args, **kwargs):
        if self.figure is None:
            self.load()

        # self.figure.add_scatter(
        #     x=df.index,
        #     y=df["pointpos"],
        #     mode="markers",
        #     marker=dict(size=5, color="MediumPurple"),
        #     name="Signal",
        # )
        self.figure.update_layout(*args, **kwargs)
        self.figure.show()
