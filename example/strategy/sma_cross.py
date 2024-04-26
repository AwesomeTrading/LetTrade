from lettrade import LetTrade, Strategy


class SmaCross(Strategy):
    n1 = 10
    n2 = 20

    def init(self):
        close = self.data.close
        # self.sma1 = self.I(SMA, close, self.n1)
        # self.sma2 = self.I(SMA, close, self.n2)
        print("close data", close)

    def next(self):
        print("-" * 64)
        print("\non next data:", self.data)
        print("\non next row:", self.data.loc[0])
        print("\non next i row:", self.data.iloc[-1])
        # if crossover(self.sma1, self.sma2):
        #     self.buy()
        # elif crossover(self.sma2, self.sma1):
        #     self.sell()


lt = LetTrade(
    strategy=SmaCross,
    csv="data/EURUSD=X.csv",
)

output = lt.run()
lt.plot()
