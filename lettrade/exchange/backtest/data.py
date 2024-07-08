import logging
import re

import pandas as pd

from lettrade.data import DataFeed

logger = logging.getLogger(__name__)


class BackTestDataFeed(DataFeed):
    """BackTest DataFeed"""

    def __init__(
        self,
        data: pd.DataFrame,
        name: str,
        timeframe: str | int | pd.Timedelta | None = None,
        meta: dict | None = None,
        since: int | str | pd.Timestamp | None = None,
        to: int | str | pd.Timestamp | None = None,
        **kwargs,
    ) -> None:
        """_summary_

        Args:
            data (pd.DataFrame): _description_
            name (str): _description_
            timeframe (str | int | pd.Timedelta | None, optional): _description_. Defaults to None.
            meta (dict | None, optional): _description_. Defaults to None.
            since (int | str | pd.Timestamp | None, optional): Drop data before since. Defaults to None.
            to (int | str | pd.Timestamp | None, optional): Drop data after to. Defaults to None.
        """
        if timeframe is None:
            timeframe = self._find_timeframe(data)
            logger.info("DataFeed %s auto detect timeframe %s", name, timeframe)
        super().__init__(
            data=data,
            name=name,
            timeframe=timeframe,
            meta=meta,
            **kwargs,
        )
        if since is not None or to is not None:
            self.drop(since=since, to=to)

    def _find_timeframe(self, df):
        if len(df.index) < 3:
            raise RuntimeError("DataFeed not enough data to detect timeframe")
        dtl = df.index
        for i in range(0, 3):
            tf = dtl[i + 1] - dtl[i]
            if tf == dtl[i + 2] - dtl[i + 1]:
                return tf
        raise RuntimeError("DataFeed cannot detect timeframe")

    def alive(self):
        return self.l.pointer_stop > 1

    def next(
        self,
        size: int = 1,
        next: pd.Timestamp | None = None,
        missing="bypass",
    ) -> bool:
        has_next = True
        if not self.is_main:
            if next is None:
                raise RuntimeError("DataFeed parameter next is None")

            size = 0
            while True:
                try:
                    dt_next = self.l.index[size + 1]
                    # No more next data
                    # if not dt_next:
                    #     has_next = False
                    #     break

                    if dt_next > next:
                        break
                    size += 1
                except (KeyError, IndexError):
                    has_next = False
                    break

            # validate
            now = self.l.index[size]
            floor = self.timeframe.floor(next)
            if now != floor and missing != "bypass":
                raise RuntimeError(
                    f"DataFeed {self.name}: jump from [{now} to {self.l.index[size+1]}]"
                    f" missing range [{floor} to {next}]",
                )

        if size > 0:
            super().next(size=size)
        return has_next


_data_name_pattern = re.compile(r"^([\w\_]+)")


def _path_to_name(path: str):
    if "/" in path:
        path = path.rsplit("/", 1)[1]
    if "." in path:
        path = path.split(".", 1)[0]

    searchs = _data_name_pattern.search(path)
    if searchs:
        path = searchs.group(1)

    return path


class CSVBackTestDataFeed(BackTestDataFeed):
    """Implement help to load DataFeed from csv file"""

    def __init__(
        self,
        path: str | None = None,
        csv: dict | None = None,
        name: str | None = None,
        timeframe: str | int | pd.Timedelta | None = None,
        meta: dict | None = None,
        data: DataFeed | None = None,
        **kwargs: dict,
    ) -> None:
        """_summary_

        Args:
            path (str | None, optional): Path to csv file. Defaults to None.
            csv (dict | None, optional): Reflect of `pandas.read_csv()` parameters. Defaults to None.
            name (str | None, optional): _description_. Defaults to None.
            timeframe (str | int | pd.Timedelta | None, optional): _description_. Defaults to None.
            meta (dict | None, optional): _description_. Defaults to None.
            data (DataFeed | None, optional): _description_. Defaults to None.
            **kwargs (dict): [DataFeed](../../data/data.md#lettrade.data.data.DataFeed) dict parameters
        """
        if name is None:
            name = _path_to_name(path)

        if data is None:
            csv_params = dict(
                index_col=0,
                parse_dates=["datetime"],
                delimiter=",",
                header=0,
            )
            if csv is not None:
                csv_params.update(**csv)

            data = pd.read_csv(path, **csv_params)

            if not isinstance(data.index, pd.DatetimeIndex):
                data.index = data.index.astype("datetime64[ns, UTC]")

        super().__init__(
            data=data,
            name=name,
            timeframe=timeframe,
            meta=meta,
            **kwargs,
        )


class YFBackTestDataFeed(BackTestDataFeed):
    """YahooFinance DataFeed"""

    def __init__(
        self,
        name: str,
        ticker: str,
        since: str,
        to: str | None = None,
        period: str | None = None,
        interval: str = "1d",
        **kwargs,
    ) -> None:
        """_summary_

        Args:
            name (str): _description_
            ticker (str): _description_
            since (str): _description_
            to (str | None, optional): _description_. Defaults to None.
            period (str | None, optional): _description_. Defaults to None.
            interval (str, optional): _description_. Defaults to "1d".
        """
        params = dict(
            start=since,
            end=to,
            period=period,
            interval=interval,
        )

        # Download
        import yfinance as yf

        df = yf.download(ticker, **params)

        # Parse to lettrade datafeed
        from .extra.yfinance import yf_parse

        df = yf_parse(df)

        # Metadata
        meta = dict(yf=dict(ticker=ticker, **params))

        super().__init__(
            name=name,
            meta=meta,
            data=df,
            **kwargs,
        )
