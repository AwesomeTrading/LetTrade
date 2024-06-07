import talib.abstract as ta

import example.logger
from lettrade import DataFeed, Strategy, crossover, crossunder
from lettrade.exchange.backtest import ForexBackTestAccount, let_backtest


class SmaCross(Strategy):
    ema1_period = 9
    ema2_period = 21

    def indicators(self, df: DataFeed):
        df["ema1"] = ta.EMA(df, timeperiod=self.ema1_period)
        df["ema2"] = ta.EMA(df, timeperiod=self.ema2_period)

        df["signal_ema_crossover"] = crossover(df.ema1, df.ema2)
        df["signal_ema_crossunder"] = crossunder(df.ema1, df.ema2)

    def next(self, df: DataFeed):
        if len(self.orders) > 0 or len(self.trades) > 0:
            return

        if df.l.signal_ema_crossover[-1]:
            price = self.data.l.close[-1]
            self.buy(size=0.1, sl=price - 0.01, tp=price + 0.01)
        elif df.l.signal_ema_crossunder[-1]:
            price = self.data.l.close[-1]
            self.sell(size=0.1, sl=price + 0.01, tp=price - 0.01)

    def stop(self, df: DataFeed):
        print(df.tail())
        print(self.orders)

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
    datas="example/data/data/EURUSD_5m-0_1000.csv",
    account=ForexBackTestAccount,
)

lt.run()
lt.plot()
