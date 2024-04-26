from lettrade import LetTrade, Strategy
from lettrade.indicator import crossover
from lettrade.indicator.buildin import SMA


class SmaCross(Strategy):
    n1 = 10
    n2 = 20

    def init(self):
        close = self.data.close
        self.sma1 = self.I(SMA, close, self.n1)
        self.sma2 = self.I(SMA, close, self.n2)

    def next(self):
        print("self.data.close", self.data.close)
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
