from pathlib import Path

import yfinance as yf

from .csv import csv_save


def yf_download(tickers, path=None, force=False, *args, **kwargs):
    # path validate
    if path is None:
        path = f"data/{tickers}.csv"

    path = Path(path)
    if not force and path.exists():
        print(f"File {path} existed")
        return

    # download
    raws = yf.download(tickers=tickers, *args, **kwargs)
    print(raws)

    # refactor
    raws = raws[raws.High != raws.Low]
    raws.reset_index(inplace=True)
    raws.head()
    raws = raws.rename(
        columns={
            "Date": "datetime",
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Volume": "volume",
        }
    )

    # save to  csv
    csv_save(raws, path=path)
