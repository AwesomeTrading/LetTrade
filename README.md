# LetTrade

[![Documentation](https://img.shields.io/badge/docs-lettrade-708FCC.svg?style=for-the-badge)](https://AwesomeTrading.github.io/LetTrade/)
[![Code Coverage](https://img.shields.io/codecov/c/gh/AwesomeTrading/lettrade.svg?style=for-the-badge)](https://codecov.io/gh/AwesomeTrading/lettrade)
[![PyPI](https://img.shields.io/pypi/v/lettrade.svg?color=blue&style=for-the-badge)](https://pypi.org/project/lettrade)
[![PyPI Python Version](https://img.shields.io/pypi/pyversions/lettrade.svg?color=skyblue&style=for-the-badge)](https://pypi.org/project/lettrade)
[![PyPI Downloads](https://img.shields.io/pypi/dd/lettrade.svg?color=skyblue&style=for-the-badge)](https://pypi.org/project/lettrade)

A lightweight trading framework compatible with Stock, Forex, Crypto... markets

Find more at [**Documentation**](https://AwesomeTrading.github.io/LetTrade/)

## Installation

> [!WARNING]  
> LetTrade is under heavy construction, features and functions may be changed.
>
> Using Developing version to get latest update.

Stable version

```sh
pip install lettrade[all]
```

Developing version

```sh
pip install 'lettrade[all] @ git+https://git@github.com/AwesomeTrading/LetTrade.git@main'
```

## Example

```python
import talib.abstract as ta

from lettrade import indicator as i
from lettrade.all import DataFeed, ForexBackTestAccount, Strategy, let_backtest


class SmaCross(Strategy):
    ema1_window = 9
    ema2_window = 21

    def indicators(self, df: DataFeed):
        df["ema1"] = ta.EMA(df, timeperiod=self.ema1_window)
        df["ema2"] = df.i.ema(period=self.ema2_window)

        df["crossover"] = i.crossover(df.ema1, df.ema2)
        df["crossunder"] = df.i.crossunder(df.ema1, df.ema2)

    def next(self, df: DataFeed):
        if df.l.crossover[-1]:
            self.positions_exit()
            self.buy(size=0.1)
        elif df.l.crossunder[-1]:
            self.positions_exit()
            self.sell(size=0.1)


lt = let_backtest(
    strategy=SmaCross,
    datas="example/data/data/EURUSD_5m-0_1000.csv",
    account=ForexBackTestAccount,
)

lt.run()
lt.plot()
```

```text
# Strategy                <class '__main__.SmaCross'>
Start                       2024-05-13 21:15:00+00:00
End                         2024-05-17 08:30:00+00:00
Duration                              3 days 11:15:00
Start Balance                                  1000.0
Equity [$]                                    1003.16
Equity Peak [$]                               1013.54
PL [$]                                           3.16
PL [%]                                           0.32
Buy & Hold PL [%]                                0.63
Max. Drawdown [%]                               -4.98
Avg. Drawdown [%]                                -1.5
Max. Drawdown Duration                1 days 16:15:00
Avg. Drawdown Duration                0 days 12:30:00
                                                     
# Positions                                        34
Win Rate [%]                                     0.38
Fee [$]                                         -1.34
Best Trade [%]                                  29.36
Worst Trade [%]                                -18.14
SQN                                              0.07
Kelly Criterion                               0.01392
Profit Factor                                1.037781
```

![Plot](https://raw.githubusercontent.com/AwesomeTrading/lettrade/main/docs/image/plot.png)

### Start a strategy

More examples can be found in [`example/`](https://github.com/AwesomeTrading/lettrade/tree/main/example)

#### Download data

```bash
python -m example.data.yfinance
```

#### Backtest strategy
```bash
python -m example.strategy.backtest_sma_cross
```

## Live Trading

### Official

- `MetaTrader`: Support MetaTrader 5 Terminal trading
- `CCXT`: [WIP] Support most of cryptocurrency exchange from CCXT library

## Development

Set up conda environment

```sh
conda create -y -n LetTrade python=3.12
conda activate LetTrade
pip install -r requirements-dev.txt
```
