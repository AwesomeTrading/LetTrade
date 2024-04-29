# LetTrade


[![Code Coverage](https://img.shields.io/codecov/c/gh/AwesomeTrading/lettrade.svg?style=for-the-badge)](https://codecov.io/gh/AwesomeTrading/lettrade)
[![PyPI](https://img.shields.io/pypi/v/lettrade.svg?color=blue&style=for-the-badge)](https://pypi.org/project/lettrade)
[![PyPI downloads](https://img.shields.io/pypi/dd/lettrade.svg?color=skyblue&style=for-the-badge)](https://pypi.org/project/lettrade)

A lightweight trading framework compatible with Stock, Forex, Crypto... markets

Inspired by `freqtrade`, `backtrader`, `backtesting.py`... 

Let make trading simpler :)

## Installation

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

from lettrade import DataFeed, LetTrade, Strategy
from lettrade.indicator import crossover


class SmaCross(Strategy):
    ema1_period = 9
    ema2_period = 21

    def indicators(self, df: DataFeed):
        df["ema1"] = ta.EMA(df, timeperiod=self.ema1_period)
        df["ema2"] = ta.EMA(df, timeperiod=self.ema2_period)
        return df

    def next(self, df: DataFeed):
        if crossover(df.ema1, df.ema2):
            self.buy(1)
        elif crossover(df.ema2, df.ema1):
            self.sell(1)

    def end(self):
        print(self.data.tail(10))


lt = LetTrade(
    strategy=SmaCross,
    csv="data/EURUSD=X_1h.csv",
)

lt.run()
lt.plot()

```

## Development

Set up conda environment
```sh
conda create -y -n LetTrade python=3.10
conda activate LetTrade
conda install -c conda-forge ta-lib
pip install -r requirements-dev.txt
```