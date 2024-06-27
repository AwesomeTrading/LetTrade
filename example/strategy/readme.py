import talib.abstract as ta

from lettrade.all import DataFeed, ForexBackTestAccount, Strategy, let_backtest


class SmaCross(Strategy):
    ema1_period = 9
    ema2_period = 21

    def indicators(self, df: DataFeed):
        df["ema1"] = ta.EMA(df, timeperiod=self.ema1_period)
        df["ema2"] = ta.EMA(df, timeperiod=self.ema2_period)

        df["crossover"] = df.i.crossover(df.ema1, df.ema2)
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
