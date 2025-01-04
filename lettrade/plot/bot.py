from typing import TYPE_CHECKING

import pandas as pd

from .plot import Plotter

if TYPE_CHECKING:
    from lettrade.account import Account
    from lettrade.bot import LetTradeBot
    from lettrade.data import DataFeed, DataFeeder
    from lettrade.exchange import Exchange
    from lettrade.strategy import Strategy

DATAFRAME_PLOTTERS_NAME = "_lt_plotters"


class BotPlotter(Plotter):
    """
    Class help to plot bot result
    """

    bot: "LetTradeBot"
    feeder: "DataFeeder"
    exchange: "Exchange"
    account: "Account"
    strategy: "Strategy"

    datas: "list[DataFeed]"
    """All plotting datafeeds"""

    _jump_since: pd.Timestamp | None = None
    _jump_to: pd.Timestamp | None = None

    def __init__(self, bot: "LetTradeBot") -> None:
        self.bot = bot
        self.feeder = bot.feeder
        self.exchange = bot.exchange
        self.account = bot.account
        self.strategy = bot.strategy

        self.datas = self.feeder.datas
        self.data = self.feeder.datas[0]

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

                loc = self.data.l.index.get_loc(order.placed_at)
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

                loc = self.data.l.index.get_loc(position.entry_at)
                since = loc - int(range / 2)
            else:  # Reset
                self.jump_reset()
                return

        elif isinstance(since, str):  # Parse string to pd.Timestamp, then since=index
            since = pd.to_datetime(since, utc=True)
            since = self.data.l.index.get_loc(since)
        elif isinstance(since, pd.Timestamp):  # Get index of Timestamp
            since = self.data.l.index.get_loc(since)

        # Since min at pointer_start
        if since < self.data.l.pointer_start:
            since = self.data.l.pointer_start
        # Since max at pointer_stop
        if since > self.data.l.pointer_stop - range:
            since = self.data.l.pointer_stop - range

        self._jump_since = self.data.l.index[since]
        self._jump_to = self.data.l.index[since + range]

        # Reload data
        self.load()

    def jump_reset(self) -> bool:
        """Reset jump datafeeds back to bot datafeeds"""
        self._jump_since = None
        self._jump_to = None
        return True
