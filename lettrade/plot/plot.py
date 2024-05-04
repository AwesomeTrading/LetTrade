import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from lettrade.account import Account
from lettrade.base import BaseDataFeeds
from lettrade.data import DataFeed, DataFeeder
from lettrade.exchange import Exchange
from lettrade.strategy import Strategy


class Plotter(BaseDataFeeds):
    figure: go.Figure = None

    _stored_datas: dict = {}

    def __init__(
        self,
        feeder: DataFeeder,
        exchange: Exchange,
        account: Account,
        strategy: Strategy,
    ) -> None:
        self.feeder: DataFeeder = feeder
        self.exchange: Exchange = exchange
        self.account: Account = account
        self.strategy: Strategy = strategy

    def load(self):
        df = self.data
        self.figure = make_subplots(
            rows=2,
            shared_xaxes=True,
            vertical_spacing=0.05,
            row_width=[0.2, 0.7],
        )
        self.figure.add_trace(
            go.Candlestick(
                x=df.index,
                open=df["open"],
                high=df["high"],
                low=df["low"],
                close=df["close"],
                name="Price",
                hoverinfo="x+y",
            ),
            row=1,
            col=1,
        )

        scratters = self.strategy.plot(df)
        if scratters:
            for s in scratters:
                self.figure.add_scatter(**s, row=1, col=1)

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

        self._plot_equity()
        self._plot_orders()
        self._plot_trades()

        self.figure.update_layout(*args, **kwargs)
        self.figure.update(layout_xaxis_rangeslider_visible=False)
        self.figure.show()

    def _plot_equity(self):
        first_index = self.data.index[0]
        x = list(first_index + i for i in self.account._equities.keys())
        y = list(e["equity"] for e in self.account._equities.values())

        self.figure.add_trace(
            go.Scatter(
                x=x,
                y=y,
                line=dict(color="#ff9900", width=2),
                showlegend=False,
            ),
            row=2,
            col=1,
        )

    def _plot_orders(self):
        orders = list(self.exchange.history_orders.values()) + list(
            self.exchange.orders.values()
        )
        first_index = self.data.index[0]
        for order in orders:
            x = [first_index + order.open_bar[0]]
            y = [order.open_price or order.limit or order.stop]
            self.figure.add_scatter(
                x=x,
                y=y,
                mode="markers",
                name=f"Order-{order.id}",
                marker=dict(
                    symbol="circle-dot",
                    size=10,
                    color="green",
                ),
                showlegend=False,
            )

    def _plot_trades(self):
        trades = list(self.exchange.history_trades.values()) + list(
            self.exchange.trades.values()
        )
        first_index = self.data.index[0]
        for trade in trades:
            # x
            x = [first_index + trade.entry_bar[0]]
            if trade.exit_bar:
                x.append(first_index + trade.exit_bar[0])

            # y
            y = [trade.entry_price]
            if trade.exit_price:
                y.append(trade.exit_price)

            color = "green" if trade.is_long else "red"
            self.figure.add_scatter(
                x=x,
                y=y,
                mode="lines+markers",
                name=f"Trade-{trade.id}",
                marker=dict(
                    symbol="circle-dot",
                    size=10,
                    color=color,
                ),
                line=dict(
                    color=color,
                    width=1,
                    dash="dash",
                ),
                showlegend=False,
            )
