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

    def stop(self):
        """stop plotter"""

    def load(self):
        df = self.data

        # Strategy plot
        config: dict = self.strategy.plot(df)

        # Params
        params = dict(
            rows=max(config.get("rows", 2), 2),
            shared_xaxes=True,
            vertical_spacing=0.03,
            row_width=[0.2, 0.7],
        )
        if "params" in config:
            params.update(**config["params"])

        # Init
        self.figure = make_subplots(**params)

        # Plot candles
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

        if "scatters" in config:
            for s in config["scatters"]:
                # s.setdefault("row", 1)
                if "row" not in s:
                    s["row"] = 1
                if "col" not in s:
                    s["col"] = 1
                self.figure.add_scatter(**s)

        # Layout
        layout_params = dict(
            title=dict(
                text=str(self.strategy),
                font=dict(size=24),
                x=0.5,
                xref="paper",
            )
        )
        if "layout" in config:
            layout_params.update(config["layout"])
        self.figure.update_layout(**layout_params)

    def jump(self, index, range=300, data: DataFeed = None):
        if data is None:
            data = self.data

        name = data.meta["name"]

        stored_data: DataFeed = self._stored_datas.setdefault(name, data)
        self.data = DataFeed(name=name, data=stored_data[index : index + range].copy())

        self.load()

    def plot(self, **kwargs):
        if self.figure is None:
            self.load()

        self._plot_equity()
        self._plot_orders()
        self._plot_trades()

        params = dict(layout_xaxis_rangeslider_visible=False)
        params.update(**kwargs)
        self.figure.update(**params)

        self.figure.show()

    def _plot_equity(self):
        first_index = self.data.index[0]
        x = list(first_index + i[0] for i in self.account._equities.keys())
        y = list(self.account._equities.values())

        # Get figure rows size
        rows, cols = self.figure._get_subplot_rows_columns()

        self.figure.add_trace(
            go.Scatter(
                x=x,
                y=y,
                line=dict(color="#ff9900", width=2),
                # showlegend=False,
                name="Equity",
            ),
            row=len(rows),
            col=1,
        )

    def _plot_orders(self):
        orders = list(self.exchange.history_orders.values()) + list(
            self.exchange.orders.values()
        )
        first_index = self.data.index[0]
        for order in orders:
            x = [first_index + order.open_at[0]]
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
            x = [first_index + trade.entry_at[0]]
            if trade.exit_at:
                x.append(first_index + trade.exit_at[0])

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
