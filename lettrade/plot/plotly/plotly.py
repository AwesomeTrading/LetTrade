from typing import Optional

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from lettrade.plot import BotPlotter, PlotColor


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
            # 0.3 for equity
            row_heights=[1] * (plot_rows - 1) + [0.3],
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
                rangeselector=dict(
                    bgcolor="#282a36",
                    activecolor="#5b5b66",
                    buttons=buttons,
                ),
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
        """Plot `equity`, `orders`, and `positions` then show"""
        if jump is not None:
            self.jump(**jump)
        elif self.figure is None:
            self.load()
        else:
            if self.jump_reset():
                self.load()

        self._plot_equity()
        self._plot_orders()
        self._plot_positions()

        params = dict(layout_xaxis_rangeslider_visible=False)
        params.update(**kwargs)
        self.figure.update(**params)

        self.figure.show()

    def _plot_equity(self):
        equities = self.account._equities

        # Filter equities in data range only
        start_dt = self.data.index[0]
        stop_dt = self.data.index[-1]
        equities = {k: e for k, e in equities.items() if k > start_dt and k < stop_dt}

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

        # Filter order in data range only
        start_dt = self.data.index[0]
        stop_dt = self.data.index[-1]
        orders = [o for o in orders if o.placed_at > start_dt and o.placed_at < stop_dt]

        # TODO: test using order/sl/tp line for performance
        for order in orders:
            x = [order.placed_at]
            y = [order.place_price]

            hovertemplate = (
                "<br>"
                # f"Order id: {order.id}<br>"
                "Index: %{x}<br>"
                f"At: {order.placed_at}<br>"
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
                    color=(PlotColor.GREEN if order.is_long else PlotColor.RED),
                ),
                showlegend=False,
            )

    def _plot_positions(self):
        positions = list(self.exchange.history_positions.values()) + list(
            self.exchange.positions.values()
        )

        # Filter equities in data range only
        start_dt = self.data.index[0]
        stop_dt = self.data.index[-1]
        _positions = []
        for p in positions:
            if p.entry_at < start_dt or p.entry_at > stop_dt:
                continue
            if p.exit_at:
                if p.exit_at < start_dt or p.exit_at > stop_dt:
                    continue
            _positions.append(p)
        positions = _positions

        for position in positions:
            x = [position.entry_at]
            y = [position.entry_price]
            customdata = [["Entry", position.size, position.pl, position.fee]]
            if position.exit_at:
                x.append(position.exit_at)
                y.append(position.exit_price)
                customdata.append(["Exit", position.size, position.pl, position.fee])

            color = PlotColor.CYAN if position.is_long else PlotColor.LIGHT_PINK
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
                    "Fee: %{customdata[3]:.2f}$<br>"
                ),
                mode="lines+markers",
                name=f"Position-{position.id}",
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
