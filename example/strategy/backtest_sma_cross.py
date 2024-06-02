import talib.abstract as ta

from example.logger import logging_filter_necessary_only
from lettrade.all import (
    CSVBackTestDataFeed,
    DataFeed,
    ForexBackTestAccount,
    Strategy,
    crossover,
    let_backtest,
)

logging_filter_necessary_only()


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
        if df.signal_ema_crossover.l[-1]:
            self.buy(size=0.1)
        elif df.signal_ema_crossunder.l[-1]:
            self.sell(size=0.1)

    # def end(self, df: DataFeed):
    #     print(df.tail(10))

    def plot(self, df: DataFeed):
        return dict(
            scatters=[
                dict(
                    x=df.datetime,
                    y=df["ema1"],
                    line=dict(color="blue", width=1),
                    name="ema1",
                ),
                dict(
                    x=df.datetime,
                    y=df["ema2"],
                    line=dict(color="green", width=1),
                    name="ema2",
                ),
            ]
        )


lt = let_backtest(
    datas=CSVBackTestDataFeed("example/data/data/EURUSD_1h.csv", name="EURUSD_1h"),
    strategy=SmaCross,
    account=ForexBackTestAccount,
)

lt.run()
lt.plot()
