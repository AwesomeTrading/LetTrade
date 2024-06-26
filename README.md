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
pip install lettrade
```

Developing version

```sh
pip install git+https://git@github.com/AwesomeTrading/LetTrade.git@main
```

## Example

```python
import talib.abstract as ta

from lettrade import indicator as i
from lettrade.all import DataFeed, ForexBackTestAccount, Strategy, let_backtest


class SmaCross(Strategy):
    ema1_period = 9
    ema2_period = 21

    def indicators(self, df: DataFeed):
        df["ema1"] = ta.EMA(df, timeperiod=self.ema1_period)
        df["ema2"] = ta.EMA(df, timeperiod=self.ema2_period)

        df["crossover"] = i.crossover(df.ema1, df.ema2)
        df["crossunder"] = i.crossunder(df.ema1, df.ema2)

    def next(self, df: DataFeed):
        if df.l.crossover[-1]:
            self.positions_exit()
            self.buy(size=0.1)
        elif df.l.crossunder[-1]:
            self.positions_exit()
            self.sell(size=0.1)


lt = let_backtest(
    strategy=SmaCross,
    datas="example/data/data/EURUSD_5m_0_1000.csv",
    account=ForexBackTestAccount,
)

lt.run()
lt.plot()
```

```text
# Strategy                       <class 'SmaCross'>
Start                     2024-05-13 21:15:00+00:00
End                       2024-05-17 08:30:00+00:00
Duration                            3 days 11:15:00
Start Balance [$]                             10000
Equity [$]                                  10000.0
PL [$]                                          0.0
PL [%]                                          0.0
Buy & Hold PL [%]                               2.0
Max. Drawdown [%]                            -33.08
Avg. Drawdown [%]                             -5.58
Max. Drawdown Duration            688 days 00:00:00
Avg. Drawdown Duration             41 days 00:00:00

# Trades                                         34
Best Trade [%]                               0.0007
Worst Trade [%]                           -0.000732
Profit Factor                                  2.13
SQN                                            1.78
```

![Plot](https://raw.githubusercontent.com/AwesomeTrading/lettrade/main/docs/image/plot.png)

### Start a strategy

More examples can be found in [`example/`](https://github.com/AwesomeTrading/lettrade/tree/main/example)

#### Download data

```bash
python -m example.data.yfinance
```

#### Backtest strategy
<!-- ```bash exec="true" source="above" result="ansi" -->
```bash
python -m example.strategy.backtest_sma_cross
```

```text
# Strategy                <class '__main__.SmaCross'>
Start                       2023-01-02 00:00:00+00:00
End                         2023-12-29 21:00:00+00:00
Duration                            361 days 21:00:00
Start Balance                                    1000
Equity [$]                                    1497.29
PL [$]                                         497.29
PL [%]                                          49.73
Buy & Hold PL [%]                                 2.0
Max. Drawdown [%]                              -33.08
Avg. Drawdown [%]                               -5.58
Max. Drawdown Duration              688 days 00:00:00
Avg. Drawdown Duration               41 days 00:00:00

# Trades                                          248
Win Rate [%]                                     50.0
Fee [$]                                         -4.96
Best Trade [%]                             554.825333
Worst Trade [%]                           -525.077316
Profit Factor                                    2.13
SQN                                              1.78
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
