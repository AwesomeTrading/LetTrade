#!/usr/bin/env python


from lettrade.exchange.backtest.data.yfinance import yf_download


def dump_csv():
    yf_download(
        "EURUSD=X",
        start="2023-01-01",
        end="2023-12-31",
        interval="1d",
        force=True,
    )


if __name__ == "__main__":
    dump_csv()
