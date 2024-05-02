import yfinance as yf

from lettrade.data import CSVDataFeed, DataFeed

from .yfinance import yf_parse


class BackTestDataFeed(DataFeed):
    def alive(self):
        return self.index.stop > 1

    def next(self, size=1) -> bool:
        self.index._range = range(
            self.index.start - size,
            self.index.stop - size,
            1,
        )
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

        # Metadata
        meta = dict(yf=dict(ticker=ticker, **params))

        super().__init__(
            name=name,
            meta=meta,
            data=df,
            *args,
            **kwargs,
        )
