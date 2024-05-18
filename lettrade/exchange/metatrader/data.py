import logging
from datetime import datetime, timezone

from lettrade.data import DataFeed

from .api import MetaTraderAPI

logger = logging.getLogger(__name__)


class MetaTraderDataFeed(DataFeed):
    def __init__(
        self,
        symbol: str,
        timeframe: str,
        feeder: "MetaTraderDataFeeder",
        api: "MetaTraderAPI",
        name: str = None,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(
            name=name or f"{symbol}_{timeframe}",
            columns=["datetime", "open", "high", "low", "close", "volume"],
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

        self.meta.update(
            dict(
                symbol=symbol,
                timeframe=timeframe,
            )
        )

        setattr(self, "__feeder", feeder)
        setattr(self, "__api", api)

    @property
    def symbol(self) -> str:
        return self.meta["symbol"]

    @property
    def timeframe(self) -> str:
        return self.meta["timeframe"]

    @property
    def _feeder(self) -> "MetaTraderDataFeeder":
        return getattr(self, "__feeder")

    @property
    def _api(self) -> "MetaTraderAPI":
        return getattr(self, "__api")

    def next(self, size=1, tick=0) -> bool:
        return self._next(size=size, tick=tick)

    def _next(self, size=1, tick=0):
        rates = self._api.rates_from_pos(
            symbol=self.symbol,
            timeframe=self.timeframe,
            since=0,
            to=size + 1,  # Get last completed bar
        )
        if len(rates) == 0:
            logger.warning("No rates data for %s", self.name)
            return False

        return self.on_rates(rates, tick=tick)

    def on_rates(self, rates, tick=0):
        i_next = 0
        if not self.empty:
            now = self.now.timestamp()

            # Remove incompleted bar
            if tick < 0:
                rates = rates[:-1]

            rates = rates[rates["time"] >= now]
            if __debug__:
                logger.info("Rates: %s", rates)

            # No new data
            if len(rates) == 0:
                return False

            # Update next bar if has new time
            if rates[0][0] > now:
                i_next = 1

        for i, rate in enumerate(rates, start=i_next):
            self.loc[
                i,
                [
                    "datetime",
                    "open",
                    "high",
                    "low",
                    "close",
                    "volume",
                ],
            ] = [
                datetime.fromtimestamp(rate[0], timezone.utc),  # datetime
                rate[1],  # open
                rate[2],  # high
                rate[3],  # low
                rate[4],  # close
                rate[5],  # volume
            ]

        self.index = range(-len(self.index) + 1, 1, 1)
        return True

    def dump_csv(self, path: str = None, since=0, to=1000):
        if self.empty:
            self._next(size=to)

        if path is None:
            path = f"data/{self.name}_{since}_{to}.csv"

        from lettrade.data.exporter.csv import csv_export

        csv_export(dataframe=self, path=path)
