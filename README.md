# Lettrade
A simple lightweight trading framework compatible with Stock, Forex, Crypto... markets

Inspired by freqtrade, backtrader, backtesting.py... 

Let make trading simpler :)

# Example
All sample in `example` directory

```python
from lettrade import LetTrade, Strategy

class SmaCross(Strategy):
    n1 = 10
    n2 = 20

    def init(self):
        self.sma1 = self.I(SMA, close, self.n1)
        self.sma2 = self.I(SMA, close, self.n2)

    def next(self):
        if crossover(self.sma1, self.sma2):
            self.buy()
        elif crossover(self.sma2, self.sma1):
            self.sell()

lt = LetTrade(
    strategy=SmaCross,
    csv="data/EURUSD=X.csv",
)

output = lt.run()
lt.plot()
```

# Development

Set up conda environment
```sh
conda create -y -n LetTrade python=3.10
conda activate LetTrade
conda install -c conda-forge ta-lib
pip install -r requirements-dev.txt
```