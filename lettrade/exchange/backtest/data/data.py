import pandas as pd
import yfinance as yf

from lettrade.data import CSVDataFeed, DataFeed

from .yfinance import yf_parse


class BackTestDataFeed(DataFeed):
    def alive(self):
        return self.index[-1] > 0

    def next(self, size=1) -> bool:
        self.index -= size
        return True


class CSVBackTestDataFeed(CSVDataFeed, BackTestDataFeed):
    pass


class YFBackTestDataFeed(BackTestDataFeed):

    def __init__(
        self,
        name,
        ticker,
        start,
        end=None,
        period=None,
        interval="1d",
        *args,
        **kwargs,
    ) -> None:
        params = dict(
            start=start,
            end=end,
            period=period,
            interval=interval,
        )

        # Download
        df = yf.download(ticker, **params)

        # Parse to lettrade datafeed
        df = yf_parse(df)

        # Reindex to 0,1,2,3...
        df.reset_index(inplace=True)

        # Information
        info = dict(ticker=ticker, **params)

        super().__init__(
            name=name,
            info=dict(yf=info),
            data=df,
            *args,
            **kwargs,
        )
