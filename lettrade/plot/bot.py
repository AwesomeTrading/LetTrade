from typing import Optional

import pandas as pd

from lettrade.account import Account
from lettrade.data import DataFeed, DataFeeder
from lettrade.exchange import Exchange
from lettrade.strategy import Strategy

from .plot import Plotter


class BotPlotter(Plotter):
    """
    Base class help to plot strategy
    """

    bot: "LetTradeBot"
    feeder: DataFeeder
    exchange: Exchange
    account: Account
    strategy: Strategy

    datas: list[DataFeed]

    _datas_stored: Optional[dict[str, DataFeed]] = None
    _jump_start_dt: Optional[pd.Timestamp] = None
    _jump_stop_dt: Optional[pd.Timestamp] = None

    def __init__(
        self,
        bot: "LetTradeBot",
    ) -> None:
        self.bot = bot
        self.feeder = bot.feeder
        self.exchange = bot.exchange
        self.account = bot.account
        self.strategy = bot.strategy

        self.datas = self.feeder.datas

    @property
    def data(self) -> DataFeed:
        return self.datas[0]

    @data.setter
    def data(self, value: DataFeed) -> None:
        self.datas[0] = value

    def jump(
        self,
        since: int | str | pd.Timestamp | None = 0,
        range: int = 300,
        name: Optional[str] = None,
    ):
        if self._datas_stored is None:
            self._datas_stored = {d.name: d for d in self.datas}

        # Reset
        if since is None:
            self.jump_reset()
        else:  # Jump to range
            if isinstance(since, str):
                since = pd.to_datetime(since, utc=True)
                since = self.data.index.get_loc(since)
            elif isinstance(since, pd.Timestamp):
                since = self.data.index.get_loc(since)

            if name is None:
                name = self.data.name

            for i, data in enumerate(self._datas_stored.values()):
                if i == 0:
                    self.datas[i] = data.__class__(
                        data=data.l[since : since + range],
                        name=data.name,
                        timeframe=data.timeframe,
                    )
                    self._jump_start_dt = self.data.index[0]
                    self._jump_stop_dt = self.data.index[-1]
                else:
                    self.datas[i] = data.__class__(
                        data=data.loc[
                            (data.index >= self._jump_start_dt)
                            & (data.index <= self._jump_stop_dt)
                        ],
                        name=data.name,
                        timeframe=data.timeframe,
                    )

        self.load()

    def jump_reset(self):
        if self._jump_start_dt is None:
            return

        self.datas = list(self._datas_stored.values())
        self._jump_start_dt = None
        self._jump_stop_dt = None
