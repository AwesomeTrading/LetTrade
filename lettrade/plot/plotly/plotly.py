from typing import Optional

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from lettrade.plot import BotPlotter


class PlotlyBotPlotter(BotPlotter):
    """
    Class help to plot `lettrade`
    """

    figure: go.Figure = None

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
                    x=data.index,
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

        self._load_extend(config)

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
            # template="plotly_dark",
            hovermode="x unified",
        )
        if "layout" in config:
            layout_params.update(config["layout"])
        self.figure.update_layout(**layout_params)

    def _load_extend(self, config: dict):
        # Plot scatter/trace
        if "scatters" in config:
            pname = f"data_{self.data.name}"
            data_config = config.setdefault(pname, {})
            data_scatters: list = data_config.setdefault("scatters", [])
            data_scatters.extend(config["scatters"])
        if "traces" in config:
            pname = f"data_{self.data.name}"
            data_config = config.setdefault(pname, {})
            data_traces: list = data_config.setdefault("traces", [])
            data_traces.extend(config["traces"])

        for data in self.datas:
            pname = f"data_{data.name}"
            if pname not in config:
                continue

            data_config = config[pname]
            data_shape = self._data_shape[data.name]

            if "scatters" in data_config:
                for scatter in data_config["scatters"]:
                    scatter.setdefault("row", data_shape["row"])
                    scatter.setdefault("col", data_shape["col"])
                    self.figure.add_scatter(**scatter)

            if "traces" in data_config:
                for trace in data_config["traces"]:
                    self.figure.add_trace(trace, **data_shape)

    def plot(self, jump: Optional[dict] = None, **kwargs):
        """Plot `equity`, `orders`, and `trades` then show"""
        if jump is not None:
            self.jump(**jump)
        elif self.figure is None:
            self.jump_reset()
            self.load()

        self._plot_equity()
        self._plot_orders()
        self._plot_trades()

        params = dict(layout_xaxis_rangeslider_visible=False)
        params.update(**kwargs)
        self.figure.update(**params)

        self.figure.show()

    def _plot_equity(self):
        equities = self.account._equities

        # Filter jump range only
        if self._jump_stop_dt is not None:
            equities = {
                k: e
                for k, e in equities.items()
                if k > self._jump_start_dt and k < self._jump_stop_dt
            }

        # Axis
        x = list(equities.keys())
        y = list(equities.values())

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

        # Filter jump range only
        if self._jump_stop_dt is not None:
            orders = [
                o
                for o in orders
                if o.open_at > self._jump_start_dt and o.open_at < self._jump_stop_dt
            ]

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

        # Filter jump range only
        if self._jump_stop_dt is not None:
            _trades = []
            for t in trades:
                if t.entry_at < self._jump_start_dt or t.entry_at > self._jump_stop_dt:
                    continue
                if t.exit_at:
                    if (
                        t.exit_at < self._jump_start_dt
                        or t.exit_at > self._jump_stop_dt
                    ):
                        continue
                _trades.append(t)
            trades = _trades

        for trade in trades:
            x = [trade.entry_at]
            y = [trade.entry_price]
            customdata = [["Entry", trade.size, trade.pl, trade.fee]]
            if trade.exit_at:
                x.append(trade.exit_at)
                y.append(trade.exit_price)
                customdata.append(["Exit", trade.size, trade.pl, trade.fee])

            color = "green" if trade.is_long else "red"
            self.figure.add_scatter(
                x=x,
                y=y,
                customdata=customdata,
                hovertemplate=(
                    "<br>"
                    "At: %{x}<br>"
                    "Price: %{y}<br>"
                    "Status: %{customdata[0]}<br>"
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
