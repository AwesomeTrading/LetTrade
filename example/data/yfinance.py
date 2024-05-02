#!/usr/bin/env python


import lettrade.logger
from lettrade.exchange.backtest.data.yfinance import yf_download


def dump_csv():
    df = yf_download(
        "EURUSD=X",
        start="2023-01-01",
        end="2023-12-31",
        interval="1h",
        force=True,
    )
    print(df)
    print(df.index)
    print(df.dtypes)


if __name__ == "__main__":
    dump_csv()
