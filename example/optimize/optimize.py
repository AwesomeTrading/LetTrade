import talib.abstract as ta

import example.logger
from lettrade.all import (
    CSVBackTestDataFeed,
    DataFeed,
    ForexBackTestAccount,
    Strategy,
    crossover,
    crossunder,
    let_backtest,
)


class SmaCross(Strategy):
    ema1_period = 9
    ema2_period = 21

    def indicators(self, df: DataFeed):
        df["ema1"] = ta.EMA(df, timeperiod=self.ema1_period)
        df["ema2"] = ta.EMA(df, timeperiod=self.ema2_period)

        df["signal_ema_crossover"] = crossover(df.ema1, df.ema2)
        df["signal_ema_crossunder"] = crossunder(df.ema1, df.ema2)
        return df

    def next(self, df: DataFeed):
        if len(self.orders) > 0 or len(self.positions) > 0:
            return

        if df.l.signal_ema_crossover[-1]:
            price = self.data.l.close[-1]
            self.buy(size=0.1, sl=price - 0.01, tp=price + 0.01)
        elif df.l.signal_ema_crossunder[-1]:
            price = self.data.l.close[-1]
            self.sell(size=0.1, sl=price + 0.01, tp=price - 0.01)

    # def on_transaction(self, transaction):
    #     print("Transaction", transaction)

    # def stop(self, df: DataFeed):
    #     print(df.tail())
    #     print(self.orders)

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


lt = let_backtest(
    strategy=SmaCross,
    datas=CSVBackTestDataFeed("example/data/data/EURUSD_5m_0_10000.csv", "EURUSD_5m"),
    account=ForexBackTestAccount,
)

# lt.run()
lt.optimize(
    ema1_period=range(5, 50),
    ema2_period=range(5, 100),
    # worker=1,
)
lt.plot()
