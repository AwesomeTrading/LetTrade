import talib.abstract as ta

from example.logger import logging_filter_necessary_only
from lettrade.all import (
    DataFeed,
    ForexBackTestAccount,
    Strategy,
    crossover,
    let_backtest,
)

logging_filter_necessary_only()


class SmaCross(Strategy):
    ema1_window = 9
    ema2_window = 21

    def indicators(self, df: DataFeed):
        df["ema1"] = ta.EMA(df, timeperiod=self.ema1_window)
        df["ema2"] = ta.EMA(df, timeperiod=self.ema2_window)

        df["signal_ema_crossover"] = crossover(df.ema1, df.ema2)
        df["signal_ema_crossunder"] = crossover(df.ema2, df.ema1)
        return df

    def next(self, df: DataFeed):
        if df.l.signal_ema_crossover[-1]:
            self.positions_exit()
            self.buy(size=0.1)
        elif df.l.signal_ema_crossunder[-1]:
            self.positions_exit()
            self.sell(size=0.1)

    # def stop(self, df: DataFeed):
    #     print(df.tail(10))

    def plot(self, df: DataFeed):
        return dict(
            scatters=[
                dict(
                    x=df.index,
                    y=df["ema1"],
                    line=dict(color="blue", width=1),
                    name="ema1",
                ),
                dict(
                    x=df.index,
                    y=df["ema2"],
                    line=dict(color="green", width=1),
                    name="ema2",
                ),
            ]
        )


if __name__ == "__main__":
    lt = let_backtest(
        datas="example/data/data/EURUSD_1h_YF_2023-01-01_2023-12-31.csv",
        strategy=SmaCross,
        account=ForexBackTestAccount,
    )

    lt.run()
    lt.plot()
