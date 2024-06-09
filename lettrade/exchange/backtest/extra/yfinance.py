import logging
from pathlib import Path

import pandas as pd
import yfinance as yf

from lettrade.data.extra.csv import csv_export

logger = logging.getLogger(__name__)


def yf_download(tickers, path=None, force=False, interval="1d", *args, **kwargs):
    # path validate
    if path is None:
        path = f"data/{tickers}_{interval}.csv"

    path = Path(path)
    if not force and path.exists():
        logger.error("File %s existed", path)
        return

    # Download
    df: pd.DataFrame = yf.download(tickers=tickers, interval=interval, *args, **kwargs)
    logger.info("YFinance downloaded:\n%s\n%s", df.head(), df.tail())

    # Parse
    df = yf_parse(df)

    # Save to csv
    return csv_export(df, path=path)


def yf_parse(df: pd.DataFrame):
    df = df[df.High != df.Low]
    df.index = df.index.rename("datetime")
    df = df.rename(
        columns={
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Volume": "volume",
        }
    )
    df = df.filter(["datetime", "open", "high", "low", "close", "volume"], axis=1)
    return df
