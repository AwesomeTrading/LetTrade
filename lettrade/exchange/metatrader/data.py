from datetime import datetime, timezone

from lettrade.data import DataFeed

from .api import MetaTraderAPI


class MetaTraderDataFeed(DataFeed):
    def __init__(
        self,
        name: str,
        ticker: str,
        timeframe: str,
        feeder: "MetaTraderDataFeeder",
        api: "MetaTraderAPI",
        *args,
        **kwargs,
    ) -> None:
        super().__init__(
            name=name,
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
                ticker=ticker,
                timeframe=timeframe,
            )
        )

        setattr(self, "__feeder", feeder)
        setattr(self, "__api", api)

    @property
    def ticker(self) -> str:
        return self.meta["ticker"]

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
            ticker=self.ticker,
            timeframe=self.timeframe,
            since=0,
            to=size + 1,  # Get last completed bar
        )

        i_next = 0
        if not self.empty:
            now = self.now.timestamp()

            # Remove incompleted bar
            if tick < 0:
                rates = rates[:-1]

            rates = rates[rates["time"] >= now]
            print("rates", rates)

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
