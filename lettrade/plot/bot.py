from typing import TYPE_CHECKING

import pandas as pd

from lettrade.account import Account
from lettrade.data import DataFeed, DataFeeder
from lettrade.exchange import Exchange
from lettrade.strategy import Strategy

from .plot import Plotter

if TYPE_CHECKING:
    from lettrade.bot import LetTradeBot

DATAFRAME_PLOTTERS_NAME = "_lt_plotters"


class BotPlotter(Plotter):
    """
    Class help to plot bot result
    """

    bot: "LetTradeBot"
    feeder: DataFeeder
    exchange: Exchange
    account: Account
    strategy: Strategy

    datas: list[DataFeed]
    """All plotting datafeeds"""

    _datas_stored: list[DataFeed] | None = None

    def __init__(self, bot: "LetTradeBot") -> None:
        self.bot = bot
        self.feeder = bot.feeder
        self.exchange = bot.exchange
        self.account = bot.account
        self.strategy = bot.strategy

        self.datas = self.feeder.datas

    @property
    def data(self) -> DataFeed:
        """Get plotting main datafeed

        Returns:
            DataFeed: _description_
        """
        return self.datas[0]

    @data.setter
    def data(self, value: DataFeed) -> None:
        self.datas[0] = value

    @property
    def _data_stored(self) -> DataFeed:
        return self._datas_stored[0]

    def jump(
        self,
        since: int | str | pd.Timestamp | None = None,
        order_id: str | None = None,
        position_id: str | None = None,
        range: int = 300,
        name: str | None = None,
    ):
        """Jump to place on datefeed

        Args:
            since (int | str | pd.Timestamp | None, optional): Jump to index/datetime. Defaults to None.
            order_id (str | None, optional): Jump to order id. Defaults to None.
            position_id (str | None, optional): Jump to position id. Defaults to None.
            range (int, optional): number of candle plot. Defaults to 300.
            name (str | None, optional): _description_. Defaults to None.

        Raises:
            RuntimeError: _description_
        """
        if self._datas_stored is None:
            self._datas_stored = self.datas.copy()

        if since is None:
            if order_id is not None:  # Jump to order id
                if not isinstance(order_id, str):
                    order_id = str(order_id)

                if order_id in self.exchange.orders:
                    order = self.exchange.orders[order_id]
                elif order_id in self.exchange.history_orders:
                    order = self.exchange.history_orders[order_id]
                else:
                    raise RuntimeError(f"Order id {order_id} not found")

                loc = self._data_stored.l.index.get_loc(order.placed_at)
                since = loc - int(range / 2)

            elif position_id is not None:  # Jump to position id
                if not isinstance(position_id, str):
                    position_id = str(position_id)

                if position_id in self.exchange.positions:
                    position = self.exchange.positions[position_id]
                elif position_id in self.exchange.history_positions:
                    position = self.exchange.history_positions[position_id]
                else:
                    raise RuntimeError(f"Position id {position_id} not found")

                loc = self._data_stored.l.index.get_loc(position.entry_at)
                since = loc - int(range / 2)
            else:  # Reset
                self.jump_reset()
                return

        elif isinstance(since, str):  # Parse string to pd.Timestamp, then since=index
            since = pd.to_datetime(since, utc=True)
            since = self._data_stored.l.index.get_loc(since)
        elif isinstance(since, pd.Timestamp):  # Get index of Timestamp
            since = self._data_stored.l.index.get_loc(since)

        if name is None:
            name = self._data_stored.name

        # Since min at pointer_start
        if since < self._data_stored.l.pointer_start:
            since = self._data_stored.l.pointer_start
        # Since max at pointer_stop
        if since > self._data_stored.l.pointer_stop - range:
            since = self._data_stored.l.pointer_stop - range

        # Jump
        jump_start_dt = None
        jump_stop_dt = None
        for i, data in enumerate(self._datas_stored):
            if i == 0:
                self.datas[i] = data.__class__(
                    data=data.l[since : since + range],
                    name=data.name,
                    timeframe=data.timeframe,
                )
                jump_start_dt = self.data.index[0]
                jump_stop_dt = self.data.index[-1]
            else:
                self.datas[i] = data.__class__(
                    data=data.loc[
                        (data.index >= jump_start_dt) & (data.index <= jump_stop_dt)
                    ],
                    name=data.name,
                    timeframe=data.timeframe,
                )

            if hasattr(data, DATAFRAME_PLOTTERS_NAME):
                object.__setattr__(
                    self.datas[i],
                    DATAFRAME_PLOTTERS_NAME,
                    getattr(data, DATAFRAME_PLOTTERS_NAME),
                )

        # Reload data
        self.load()

    def jump_reset(self) -> bool:
        """Reset jump datafeeds back to bot datafeeds"""
        if not self._datas_stored or self.data is self._data_stored:
            return False

        self.datas = self._datas_stored.copy()
        return True
