import logging
from datetime import datetime
from typing import Optional, Type

import pandas as pd
from lettrade.data import DataFeed

from .api import LiveAPI

logger = logging.getLogger(__name__)


class LiveDataFeed(DataFeed):
    _api_cls: Type[LiveAPI] = LiveAPI

    def __init__(
        self,
        symbol: str,
        timeframe: str | int | pd.Timedelta,
        name: Optional[str] = None,
        api: Optional[LiveAPI] = None,
        **kwargs,
    ) -> None:
        super().__init__(
            name=name or f"{symbol}_{timeframe}",
            timeframe=timeframe,
            columns=["open", "high", "low", "close", "volume"],
            **kwargs,
        )
        self.meta.update(dict(symbol=symbol))

        if api is not None:
            self._api = api

    # Properties
    @property
    def symbol(self) -> str:
        return self.meta["symbol"]

    @property
    def _api(self) -> LiveAPI:
        return getattr(self, "__api")

    @_api.setter
    def _api(self, value) -> LiveAPI:
        object.__setattr__(self, "__api", value)

    # Functions
    def copy(self, deep: bool = False, **kwargs) -> DataFeed:
        return super().copy(deep, symbol=self.symbol, **kwargs)

    def next(self, size=1, tick=0) -> bool:
        self.bars_load(since=0, to=size + 1)
        self.l.go_stop()
        return True

    def bars_load(
        self,
        since: int | str | pd.Timestamp,
        to: int | str | pd.Timestamp,
    ) -> bool:
        """Get bar and push to DataFeed

        Args:
            since (int | str | pd.Timestamp): _description_
            to (int | str | pd.Timestamp): _description_

        Returns:
            bool: True if has data, False if no data
        """
        bars = self.bars(since=since, to=to)

        if len(bars) == 0:
            logger.warning("No bars data for %s", self.name)
            return False

        self.push(bars)
        return True

    def bars(
        self,
        since: int | str | pd.Timestamp,
        to: int | str | pd.Timestamp,
    ) -> list:
        """Get bars from LiveAPI

        Args:
            since (int | str | pd.Timestamp): _description_
            to (int | str | pd.Timestamp): _description_

        Returns:
            list: list of bar
        """
        return self._api.bars(
            symbol=self.symbol,
            timeframe=self.timeframe.string,
            since=since,
            to=to,
        )

    ### Extend
    def dump_csv(
        self,
        path: Optional[str] = None,
        since: Optional[int | str | datetime] = 0,
        to: Optional[int | str | datetime] = 1_000,
    ):
        if self.empty:
            if isinstance(since, str):
                since = pd.to_datetime(since).to_pydatetime()
            if isinstance(to, str):
                to = pd.to_datetime(to).to_pydatetime()

            self.bars_load(since=since, to=to)

        if path is None:
            path = f"data/{self.name}-{since}_{to}.csv"

        from lettrade.data.extra.csv import csv_export

        csv_export(dataframe=self, path=path)

    @classmethod
    def instance(
        cls,
        api: Optional[LiveAPI] = None,
        api_kwargs: Optional[dict] = None,
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
            api = cls._api_cls(**api_kwargs)
        obj = cls(api=api, **kwargs)
        return obj
