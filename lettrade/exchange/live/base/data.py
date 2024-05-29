import logging
from datetime import datetime, timezone
from typing import Type

import pandas as pd

from lettrade.data import DataFeed

from .api import LiveAPI

logger = logging.getLogger(__name__)


class LiveDataFeed(DataFeed):
    api_cls: Type[LiveAPI] = LiveAPI

    def __init__(
        self,
        symbol: str,
        timeframe: str | int | pd.Timedelta,
        name: str = None,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(
            name=name or f"{symbol}_{timeframe}",
            timeframe=timeframe,
            columns=["open", "high", "low", "close", "volume"],
            # dtype=[
            #     ("datetime", "datetime64[ns]"),
            #     ("open", "float64"),
            #     ("high", "float64"),
            #     ("low", "float64"),
            #     ("close", "float64"),
            #     ("volume", "float64"),
            # ],
            *args,
            **kwargs,
        )
        # self["datetime"] = pd.to_datetime(self["datetime"])

        self.meta.update(dict(symbol=symbol))

    @property
    def symbol(self) -> str:
        return self.meta["symbol"]

    @property
    def _api(self) -> LiveAPI:
        return getattr(self, "__api")

    @_api.setter
    def _api(self, value) -> LiveAPI:
        setattr(self, "__api", value)

    def next(self, size=1, tick=0) -> bool:
        return self._next(size=size, tick=tick)

    def _next(self, size=1, tick=0):
        rates = self._api.bars(
            symbol=self.symbol,
            timeframe=self.timeframe.string,
            since=0,
            to=size + 1,  # Get last completed bar
        )
        if len(rates) == 0:
            logger.warning("No rates data for %s", self.name)
            return False

        return self.on_rates(rates, tick=tick)

    def on_rates(self, rates, tick=0):
        self.push(rates)
        self.index.go_end()
        return True

    def dump_csv(self, path: str = None, since=0, to=1000):
        if self.empty:
            self._next(size=to)

        if path is None:
            path = f"data/{self.name}-{since}_{to}.csv"

        from lettrade.data.extra.csv import csv_export

        csv_export(dataframe=self, path=path)

    @classmethod
    def instance(
        cls,
        api: LiveAPI = None,
        api_kwargs: dict = None,
        **kwargs,
    ) -> "LiveDataFeed":
        """_summary_

        Args:
            api (LiveAPI, optional): _description_. Defaults to None.
            api_kwargs (dict, optional): _description_. Defaults to None.

        Raises:
            RuntimeError: Missing api requirement

        Returns:
            LiveDataFeed: DataFeed object
        """
        if api is None:
            if api_kwargs is None:
                raise RuntimeError("api or api_kwargs cannot missing")
            api = cls.api_cls(**api_kwargs)
        data = cls(**kwargs)
        data._api = api
        return data
