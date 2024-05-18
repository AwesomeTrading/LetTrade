# LetTrade


[![Code Coverage](https://img.shields.io/codecov/c/gh/AwesomeTrading/lettrade.svg?style=for-the-badge)](https://codecov.io/gh/AwesomeTrading/lettrade)
[![PyPI](https://img.shields.io/pypi/v/lettrade.svg?color=blue&style=for-the-badge)](https://pypi.org/project/lettrade)
[![PyPI Python Version](https://img.shields.io/pypi/pyversions/lettrade.svg?color=skyblue&style=for-the-badge)](https://pypi.org/project/lettrade)
[![PyPI Downloads](https://img.shields.io/pypi/dd/lettrade.svg?color=skyblue&style=for-the-badge)](https://pypi.org/project/lettrade)

A lightweight trading framework compatible with Stock, Forex, Crypto... markets

Inspired by `freqtrade`, `backtrader`, `backtesting.py`... 

Let make algo trading simple :)

## Installation

Stable version
```sh
pip install lettrade
```

Developing version
```sh
pip install git+https://git@github.com/AwesomeTrading/lettrade.git@main
```

## Example
All sample are in `example/` directory

```python
import talib.abstract as ta

from lettrade import DataFeed, LetTrade, Strategy, let_backtest
from lettrade.indicator import crossover, crossunder


class SmaCross(Strategy):
    ema1_period = 9
    ema2_period = 21

    def indicators(self, df: DataFeed):
        df["ema1"] = ta.EMA(df, timeperiod=self.ema1_period)
        df["ema2"] = ta.EMA(df, timeperiod=self.ema2_period)

        df["crossover"] = crossover(df.ema1, df.ema2)
        df["crossunder"] = crossunder(df.ema1, df.ema2)

    def next(self, df: DataFeed):
        if df.crossover[-1]:
            self.buy(1)
        elif df.crossunder[-1]:
            self.sell(1)

    def end(self, df: DataFeed):
        print(df.tail(10))


lt = let_backtest(
    strategy=SmaCross,
    datas="data/EURUSD=X_1h.csv",
)

lt.run()
lt.plot()

```

## Live Trading
### Official
- `MetaTrader`: Support MetaTrader 5 Terminal trading
- `CCXT`: Support most of cryptocurrency exchange from CCXT library

## Development

Set up conda environment
```sh
conda create -y -n LetTrade python=3.10
conda activate LetTrade
conda install -c conda-forge ta-lib
pip install -r requirements-dev.txt
```