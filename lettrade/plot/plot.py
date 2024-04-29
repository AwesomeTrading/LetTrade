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

    def __init__(self, feeder: DataFeeder, data: list[go.Scatter] = []) -> None:
        self.feeder: DataFeeder = feeder
        self.plot_data: list[go.Scatter] = data

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
                *self.plot_data,
            ]
        )
        # self.figure.update_layout(hovermode="x unified")

    def jump(self, index, range=300, data: DataFeed = None):
        if data is None:
            data = self.data

        name = data.meta["name"]

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
