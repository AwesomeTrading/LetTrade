import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from lettrade.data import DataFeed
from lettrade.plot import BotPlotter, PlotColor


class PlotlyBotPlotter(BotPlotter):
    """Class help to plot `lettrade`"""

    figure: go.Figure = None

    _data_shape: dict

    def stop(self):
        """stop plotter"""

    def _config_default(self):
        """Generate default config

        Example:
            ```json
            {
                "groups": [
                    {
                        "id": "EURUSD_5m",
                        "type": "data",
                        "data": pandas.DataFrame,
                        "height": 1,
                        "items": [
                            {
                                "type": "candlestick",
                                "show_orders": True,
                                "show_positions": True,
                                "update_xaxes": {
                                    "title_text": "EURUSD_5m",
                                    "rangeslider_visible": False,
                                    "mirror": True,
                                    "ticks": "outside",
                                    "showline": True
                                },
                                "update_yaxes": {
                                    "title_text": "Price $",
                                    "mirror": True,
                                    "ticks": "outside",
                                    "showline": True
                                }
                            },
                            {
                                "type": "scatter",
                                "x": pandas.DatetimeIndex,
                                "y": pandas.Series,
                                "line": { "color": <PlotColor.AMBER: '#fa0'>, "width": 1 },
                                "name": "ema1",
                                "mode": "lines"
                            },
                            {
                                "type": "scatter",
                                "x": pandas.DatetimeIndex,
                                "y": pandas.Series,
                                "line": { "color": <PlotColor.CYAN: '#00bad6'>, "width": 1 },
                                "name": "ema2",
                                "mode": "lines"
                            }
                        ]
                    },
                    { "id": "equity", "type": "equity", "height": 0.5 }
                ],
                "params": {
                    "shared_xaxes": True,
                    "vertical_spacing": 0.03,
                    "rows": 2,
                    "row_heights": [1, 0.5]
                },
                "layout": {
                    "xaxis": {
                        "rangeselector": {
                            "bgcolor": "#282a36",
                            "activecolor": "#5b5b66",
                            "buttons": [
                            { "step": "all" },
                            {
                                "count": 6,
                                "label": "6 day",
                                "step": "day",
                                "stepmode": "backward"
                            },
                            {
                                "count": 3,
                                "label": "3 day",
                                "step": "day",
                                "stepmode": "backward"
                            },
                            {
                                "count": 1,
                                "label": "1 day",
                                "step": "day",
                                "stepmode": "backward"
                            }
                            ]
                        }
                    },
                    "yaxis": { "autorange": True, "fixedrange": False },
                    "title": {
                        "text": "<__main__.SmaCross object at 0x709c53ee4d70>",
                        "font": { "size": 24 },
                        "x": 0.5,
                        "xref": "paper"
                    },
                    "modebar_add": [
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
                        "eraseshape"
                    ],
                    "hovermode": "x unified"
                },
                "shapes": {
                    "EURUSD_5m": { "group_index": 0, "rows": 1, "cols": 1 },
                    "equity": { "group_index": 1, "rows": 1, "cols": 1 }
                },
                "rows_total": 2,
                "cols_total": 2
            }
            ```

        Returns:
            _type_: _description_
        """
        # --- Data
        groups = []
        for data in self.datas:
            groups.append(
                dict(
                    id=data.name,
                    type="data",
                    data=data,
                    height=1,
                    items=[
                        dict(
                            type="candlestick",
                            name=data.name,
                            show_orders=data is self.data,
                            show_positions=data is self.data,
                            update_xaxes=dict(
                                title_text=data.name,
                                rangeslider_visible=False,
                                # showspikes=True,
                                # spikemode="across",
                                mirror=True,
                                ticks="outside",
                                showline=True,
                                # linecolor="",
                            ),
                            update_yaxes=dict(
                                title_text="Price $",
                                # autorange=True,
                                # fixedrange=False,
                                # showspikes=True,
                                # spikemode="across",
                                mirror=True,
                                ticks="outside",
                                showline=True,
                            ),
                        )
                    ],
                )
            )

        # --- Equity
        groups.append(
            dict(
                id="equity",
                type="equity",
                row_height=0.5,
            )
        )

        # --- Buttons
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
        return dict(
            groups=groups,
            # --- Params
            params=dict(
                shared_xaxes=True,
                vertical_spacing=0.03,
            ),
            # --- Layout
            layout=dict(
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
                height=1_000 * len(self.datas),
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
            ),
        )

    def _config_strategy(self, config: dict):
        """Merge strategy plot config"""
        strategy_config: dict = self.strategy._plot(*self.datas)

        # Move global items to main data items
        group_indexes = list(group["id"] for group in config["groups"])
        if "items" in strategy_config:
            group_index = group_indexes.index(self.data.name)
            data_group = config["groups"][group_index]
            data_items: list = data_group.setdefault("items", [])
            data_items.extend(strategy_config["items"])

        for data in self.datas:
            dname = data.name
            if dname not in strategy_config:
                continue

            group_index = group_indexes.index(data.name)
            data_group = config["groups"][group_index]
            data_config = strategy_config[dname]

            data_items: list = data_group.setdefault("items", [])
            data_items.extend(data_config["items"])

        if "layout" in strategy_config:
            config["layout"].update(strategy_config["layout"])

        return config

    def _config_standard(self, config: dict):
        """Calculate shapes/heights"""
        shapes = dict()
        rows_total = 1
        cols_total = 1
        row_heights = []
        for i, group in enumerate(config["groups"]):
            if group["type"] == "data":
                _rows = []
                _cols = []
                _heights = dict()
                for item in group["items"]:
                    row = item.get("row", 1)
                    _rows.append(row)
                    _cols.append(item.get("col", 1))
                    _heights[row] = item.pop("row_height", 1)

                rows = max(_rows)
                cols = max(_cols)

                for j in range(1, rows):
                    if j not in _heights.values():
                        _heights[j] = 1

                row_heights += _heights.values()
            else:
                rows = group.get("row", 1)
                cols = group.get("col", 1)
                row_heights += [group.pop("row_height", 1)]

            shapes[group["id"]] = dict(
                group_index=i,
                row=rows_total,
                col=cols_total,
                rows=rows,
                cols=cols,
            )
            rows_total += rows
            cols_total = cols

        params: dict = config.setdefault("params", dict())

        # rows -1: because row index start at 1
        params.update(rows=rows_total - 1, row_heights=row_heights)

        config.update(
            params=params,
            shapes=shapes,
            rows_total=rows_total,
            cols_total=cols_total,
        )
        return config

    def _plot_config(self, config: dict):
        """Apply config to figure"""
        rows = 0
        for group in config["groups"]:
            group_shape = config["shapes"][group["id"]]

            if group["type"] == "data":
                for item in group["items"]:
                    row = rows + item.pop("row", 1)
                    col = item.pop("col", 1)

                    match item["type"]:
                        case "candlestick":
                            self._plot_candlestick(
                                data=group["data"],
                                row=row,
                                col=col,
                                **item,
                            )
                        case "scatter":
                            self._plot_scatter(
                                data=group["data"],
                                row=row,
                                col=col,
                                **item,
                            )
            elif group["type"] == "equity":
                row = rows + group.pop("row", 1)
                col = group.pop("col", 1)

                self._plot_equity(row=row, col=col, **group)

            rows += group_shape["rows"]

    def _plot_candlestick(
        self,
        data: DataFeed,
        x=None,
        open=None,
        high=None,
        low=None,
        close=None,
        update_xaxes: dict | None = None,
        update_yaxes: dict | None = None,
        show_orders: bool = False,
        show_positions: bool = False,
        row: int = 1,
        col: int = 1,
        type: str | None = None,
        **kwargs,
    ):
        self.figure.add_trace(
            go.Candlestick(
                x=x if x is not None else data.index,
                open=open if open is not None else data["open"],
                high=high if high is not None else data["high"],
                low=low if low is not None else data["low"],
                close=close if close is not None else data["close"],
                **kwargs,
            ),
            row=row,
            col=col,
        )
        if update_xaxes is not None:
            self.figure.update_xaxes(row=row, col=col, **update_xaxes)
        if update_yaxes is not None:
            self.figure.update_yaxes(row=row, col=col, **update_yaxes)
        if show_orders:
            self._plot_orders(data=data, row=row, col=col)
        if show_positions:
            self._plot_positions(data=data, row=row, col=col)

    def _plot_scatter(
        self,
        data: DataFeed,
        x: pd.Index,
        y: pd.Series,
        row: int = 1,
        col: int = 1,
        fullfill: bool = False,
        type: str | None = None,
        **kwargs,
    ):
        # Fill None
        if fullfill and x is not data.index:
            s = pd.Series(None, index=data.index)
            s.loc[x] = y
            x = s.index
            y = s

        self.figure.add_scatter(x=x, y=y, row=row, col=col, **kwargs)

    def _plot_equity(
        self,
        row: int = 1,
        col: int = 1,
        type: str | None = None,
        **kwargs,
    ):
        equities = self.account._equities

        # Filter equities in data range only
        start_dt = self.data.index[0]
        stop_dt = self.data.index[-1]
        equities = {k: e for k, e in equities.items() if k > start_dt and k < stop_dt}

        if len(equities) == 0:
            return

        # Axis
        x = list(equities.keys())
        y = list(equities.values())

        self.figure.add_trace(
            go.Scatter(
                x=x,
                y=y,
                line=dict(color="#ff9900", width=2),
                # showlegend=False,
                name="Equity",
                # fill="toself",
            ),
            row=row,
            col=col,
        )
        self.figure.update_yaxes(
            title_text="Equity",
            row=row,
            col=col,
        )

    def _plot_orders(
        self,
        data: DataFeed,
        row: int = 1,
        col: int = 1,
    ):
        orders = list(self.exchange.history_orders.values()) + list(
            self.exchange.orders.values()
        )

        # Filter order in data range only
        start_dt = data.index[0]
        stop_dt = data.index[-1]
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
                row=row,
                col=col,
            )

    def _plot_positions(
        self,
        data: DataFeed,
        row: int = 1,
        col: int = 1,
    ):
        positions = list(self.exchange.history_positions.values()) + list(
            self.exchange.positions.values()
        )

        # Filter equities in data range only
        start_dt = data.index[0]
        stop_dt = data.index[-1]
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
                row=row,
                col=col,
            )

    def load(self):
        """Load plot config from `Strategy.plot()` and setup candlestick/equity"""

        config = self._config_default()
        config = self._config_strategy(config)
        config = self._config_standard(config)

        params: dict = config.setdefault("params", dict())
        self.figure = make_subplots(**params)

        self._plot_config(config)

        self.figure.update_layout(**config["layout"])

    def plot(self, jump: dict | None = None, **kwargs):
        """Plotly show figure

        Args:
            jump (dict | None, optional): _description_. Defaults to None.
        """
        if jump is not None:
            self.jump(**jump)
        elif self.figure is None:
            self.load()
        else:
            if self.jump_reset():
                self.load()

        params = dict(layout_xaxis_rangeslider_visible=False)
        params.update(**kwargs)
        self.figure.update(**params)

        self.figure.show()
