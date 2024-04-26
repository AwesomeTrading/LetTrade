from lettrade import LetTrade, Strategy


class SmaCross(Strategy):
    n1 = 10
    n2 = 20

    def init(self):
        close = self.data.Close
        # self.sma1 = self.I(SMA, close, self.n1)
        # self.sma2 = self.I(SMA, close, self.n2)

    def next(self):
        pass
        # if crossover(self.sma1, self.sma2):
        #     self.buy()
        # elif crossover(self.sma2, self.sma1):
        #     self.sell()


lt = LetTrade(
    strategy=SmaCross,
    csv="data/EURUSD=X.csv",
    cash=10000,
    commission=0.002,
    exclusive_orders=True,
)

output = lt.run()
lt.plot()
