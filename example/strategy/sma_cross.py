import talib.abstract as ta

from lettrade import DataFeed, LetTrade, Strategy
from lettrade.indicator import crossover


class SmaCross(Strategy):
    ema1_period = 9
    ema2_period = 21

    def init(self):
        pass

    def indicators(self, df: DataFeed):
        df["ema1"] = ta.EMA(df, timeperiod=self.ema1_period)
        df["ema2"] = ta.EMA(df, timeperiod=self.ema2_period)

        self.sma1 = df["ema1"]
        self.sma2 = df["ema2"]

        return df

    def next(self, df):
        print("-" * 64)
        print("self.data.close:")
        print(self.data.close[0])
        print("self.sma1:")
        print(self.sma1[-1])

        if crossover(self.sma1, self.sma2):
            self.buy(1)
        elif crossover(self.sma2, self.sma1):
            self.sell(1)

    def end(self):
        print("*" * 64)
        print(self.data.tail(10))


lt = LetTrade(
    strategy=SmaCross,
    csv="data/EURUSD=X.csv",
)

lt.run()
lt.plot()
