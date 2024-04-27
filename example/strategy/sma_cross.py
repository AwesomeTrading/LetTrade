import talib.abstract as ta

import lettrade.logger
from lettrade import DataFeed, LetTrade, Strategy
from lettrade.indicator.buildin import crossover


class SmaCross(Strategy):
    ema1_period = 9
    ema2_period = 21

    def indicators(self, df: DataFeed):
        df["ema1"] = ta.EMA(df, timeperiod=self.ema1_period)
        df["ema2"] = ta.EMA(df, timeperiod=self.ema2_period)

        df["signal_ema_crossover"] = crossover(df.ema1, df.ema2)
        df["signal_ema_crossunder"] = crossover(df.ema2, df.ema1)
        return df

    def next(self, df: DataFeed):
        if df.signal_ema_crossover[0]:
            self.buy(size=0.1)
        elif df.signal_ema_crossunder[0]:
            self.sell(size=0.1)

    def end(self):
        print("*" * 64)
        print(self.data.tail(10))


lt = LetTrade(
    strategy=SmaCross,
    csv="data/EURUSD=X_1h.csv",
)

lt.run()
lt.plot()
