from pathlib import Path

import yfinance as yf

from .csv import csv_save


def yf_download(tickers, path=None, force=False, interval="1d", *args, **kwargs):
    # path validate
    if path is None:
        path = f"data/{tickers}_{interval}.csv"

    path = Path(path)
    if not force and path.exists():
        print(f"File {path} existed")
        return

    # download
    raws = yf.download(tickers=tickers, interval=interval, *args, **kwargs)
    print(raws)

    # refactor
    raws = raws.drop("Adj Close", axis=1)
    raws = raws[raws.High != raws.Low]
    raws.reset_index(inplace=True)
    raws.head()
    raws = raws.rename(
        columns={
            "Datetime": "datetime",
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Volume": "volume",
        }
    )

    # save to  csv
    csv_save(raws, path=path)
