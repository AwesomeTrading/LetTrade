import plotly.graph_objects as go
from plotly.subplots import make_subplots

from lettrade.plot import Plotter


class PlotlyPlotter(Plotter):
    """
    Class help to plot `lettrade`
    """

    figure: go.Figure = None

    _datas_stored: dict = {}
    _data_shape: dict

    def stop(self):
        """stop plotter"""

    def load(self):
        """Load plot config from `Strategy.plot()` and setup candlestick/equity"""

        # Strategy plot
        config: dict = self.strategy.plot(*self.datas)

        # Params
        plot_rows = max(config.get("rows", 2), len(self.datas) + 1)
        params = dict(
            rows=plot_rows,
            shared_xaxes=True,
            vertical_spacing=0.03,
            # row_width=[0.2, 0.7],
        )
        if "params" in config:
            params.update(**config["params"])

        # Init
        self.figure = make_subplots(**params)

        # Plot candles
        self._data_shape = dict()
        for i, data in enumerate(self.datas):
            shape = dict(
                row=1 + i,
                col=1,
            )
            self._data_shape[data.name] = shape
            self.figure.add_trace(
                go.Candlestick(
                    x=data.datetime,
                    open=data["open"],
                    high=data["high"],
                    low=data["low"],
                    close=data["close"],
                    name=f"Price {data.name}",
                    # hoverinfo="x+y",
                ),
                **shape,
            )
            self.figure.update_yaxes(
                title_text="Price $",
                # autorange=True,
                # fixedrange=False,
                # showspikes=True,
                # spikemode="across",
                mirror=True,
                ticks="outside",
                showline=True,
                # linecolor="",
                **shape,
            )
            self.figure.update_xaxes(
                title_text=data.name,
                rangeslider_visible=False,
                # showspikes=True,
                # spikemode="across",
                mirror=True,
                ticks="outside",
                showline=True,
                # linecolor="",
                **shape,
            )

        if "scatters" in config:
            scatters = config["scatters"]
            if isinstance(scatters, list):
                for s in scatters:
                    s.setdefault("row", 1)
                    s.setdefault("col", 1)
                    self.figure.add_scatter(**s)
            elif isinstance(scatters, dict):
                for name, ss in scatters.items():
                    shape = self._data_shape[name]
                    for s in ss:
                        self.figure.add_scatter(**s, **shape)

        # Buttons
        buttons = [dict(step="all")]
        match self.data.timeframe.unit:
            case "m":
                count = 1
                step = "day"
            case "h":
                count = 7
                step = "day"
            case _:
                count = 1
                step = "month"
        buttons.extend(
            [
                dict(
                    count=6 * count,
                    label=f"{6*count} {step}",
                    step=step,
                    stepmode="backward",
                ),
                dict(
                    count=3 * count,
                    label=f"{3*count} {step}",
                    step=step,
                    stepmode="backward",
                ),
                dict(
                    count=count,
                    label=f"{count} {step}",
                    step=step,
                    stepmode="backward",
                ),
            ]
        )

        # Layout
        layout_params = dict(
            xaxis=dict(
                rangeselector=dict(buttons=buttons),
            ),
            yaxis=dict(
                autorange=True,
                fixedrange=False,
            ),
            title=dict(
                text=str(self.strategy),
                font=dict(size=24),
                x=0.5,
                xref="paper",
            ),
            # autosize=False,
            # width=800,
            height=1_000 * plot_rows,
            modebar_add=[
                "v1hovermode",
                "hoverclosest",
                "hovercompare",
                "togglehover",
                "togglespikelines",
                "drawline",
                "drawopenpath",
                "drawclosedpath",
                "drawcircle",
                "drawrect",
                "eraseshape",
            ],
            template="plotly_dark",
            hovermode="x unified",
        )
        if "layout" in config:
            layout_params.update(config["layout"])
        self.figure.update_layout(**layout_params)

    def plot(self, **kwargs):
        """Plot `equity`, `orders`, and `trades` then show"""
        if self.figure is None:
            self.load()

        self._plot_equity()
        self._plot_orders()
        self._plot_trades()

        params = dict(layout_xaxis_rangeslider_visible=False)
        params.update(**kwargs)
        self.figure.update(**params)

        if __debug__:
            if self._docs_plot(**kwargs):
                return

        self.figure.show()

    def _plot_equity(self):
        x = list(self.account._equities.keys())
        y = list(self.account._equities.values())

        # Get figure rows size
        row_length = len(self.figure._get_subplot_rows_columns()[0])

        self.figure.add_trace(
            go.Scatter(
                x=x,
                y=y,
                line=dict(color="#ff9900", width=2),
                # showlegend=False,
                name="Equity",
                # fill="toself",
            ),
            row=row_length,
            col=1,
        )
        self.figure.update_yaxes(
            title_text="Equity",
            row=row_length,
            col=1,
        )

    def _plot_orders(self):
        orders = list(self.exchange.history_orders.values()) + list(
            self.exchange.orders.values()
        )
        for order in orders:
            x = [order.open_at]
            y = [order.open_price or order.limit or order.stop]

            hovertemplate = (
                f"Order id: {order.id}<br>"
                "Index: %{x}<br>"
                f"At: {order.open_at}<br>"
                "Price: %{y}<br>"
                f"Size: {order.size}<br>"
            )
            if order.sl:
                hovertemplate += f"SL: {order.sl}<br>"
            if order.tp:
                hovertemplate += f"TP: {order.tp}<br>"

            self.figure.add_scatter(
                x=x,
                y=y,
                hovertemplate=hovertemplate,
                mode="markers",
                name=f"Order-{order.id}",
                marker=dict(
                    symbol="line-ew-open",
                    size=10,
                    color="green" if order.is_long else "red",
                ),
                showlegend=False,
            )

    def _plot_trades(self):
        trades = list(self.exchange.history_trades.values()) + list(
            self.exchange.trades.values()
        )
        for trade in trades:
            x = [trade.entry_at]
            y = [trade.entry_price]
            customdata = [[trade.entry_at, trade.size, trade.pl, trade.fee]]
            if trade.exit_at:
                x.append(trade.exit_at)
                y.append(trade.exit_price)
                customdata.append([trade.exit_at, trade.size, trade.pl, trade.fee])

            color = "green" if trade.is_long else "red"
            self.figure.add_scatter(
                x=x,
                y=y,
                customdata=customdata,
                hovertemplate=(
                    f"Trade id: {trade.id}<br>"
                    "Index: %{x}<br>"
                    "At: %{customdata[0]}<br>"
                    "Price: %{y}<br>"
                    "Size: %{customdata[1]}<br>"
                    "PL: %{customdata[2]:.2f}$<br>"
                    "Fee: %{customdata[3]:.2f}$"
                ),
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

    def _docs_plot(self, **kwargs):
        if __debug__:
            from lettrade.utils.docs import is_docs_session

            if not is_docs_session():
                return

            # self.figure.to_html(full_html=False, include_plotlyjs="cdn")
            return True
