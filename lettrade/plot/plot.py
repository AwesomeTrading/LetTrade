import numpy as np
import pandas as pd
import plotly.graph_objects as go

from lettrade.base import BaseDataFeeds
from lettrade.data import DataFeed, DataFeeder
from lettrade.exchange import Exchange


class Plotter(BaseDataFeeds):
    figure: go.Figure = None

    _stored_datas: dict = {}

    def __init__(
        self, feeder: DataFeeder, exchange: Exchange, data: list[go.Scatter] = []
    ) -> None:
        self.feeder: DataFeeder = feeder
        self.exchange: Exchange = exchange
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

        self._plot_orders()
        # self._plot_trades()

        self.figure.update_layout(*args, **kwargs)
        self.figure.show()

    def _plot_orders(self):
        orders = pd.concat([self.exchange.history_orders, self.exchange.orders])
        first_index = self.data.index[0]
        for order in orders.to_list():
            x = [first_index - order.open_bar]
            y = [order.open_price or order.limit or order.stop]
            self.figure.add_scatter(
                x=x,
                y=y,
                mode="markers",
                name="Order",
                marker=dict(
                    symbol="circle-dot",
                    size=10,
                    color="green",
                ),
            )

    def _plot_trades(self):
        trades = pd.concat([self.exchange.history_trades, self.exchange.trades])
        first_index = self.data.index[0]
        for trade in trades.to_list():
            # x
            x = [first_index - trade.open_bar]
            if trade.close_bar:
                x.append(first_index - trade.close_bar)

            # y
            y = [trade.open_price]
            if trade.close_price:
                y.append(first_index - trade.close_price)

            self.figure.add_scatter(
                x=x,
                y=y,
                mode="lines+markers",
                name="Order",
                marker=dict(
                    symbol="circle-dot",
                    size=10,
                    color="royalblue",
                ),
                line=dict(
                    color="royalblue",
                    width=1,
                    dash="dash",
                ),
            )
