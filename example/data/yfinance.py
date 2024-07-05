#!/usr/bin/env python


import example.logger
from lettrade.exchange.backtest.extra.yfinance import yf_download


def dump_csv():
    since = "2023-01-01"
    to = "2023-12-31"

    path = f"example/data/data/EURUSD_1h_YF_{since}_{to}.csv"

    df = yf_download(
        "EURUSD=X",
        since=since,
        to=to,
        interval="1h",
        path=path,
        force=True,
    )
    print(df)
    print(df.index)
    print(df.dtypes)


if __name__ == "__main__":
    dump_csv()
