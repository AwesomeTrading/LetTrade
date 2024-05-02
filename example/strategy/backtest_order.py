import pandas as pd
import talib.abstract as ta

import lettrade.logger
from lettrade import DataFeed, LetTrade, Strategy
from lettrade.exchange import Order
from lettrade.indicator import crossover, crossunder


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
        # if self.orders.size > 0 or self.trades.size > 0:
        #     return

        if df.signal_ema_crossover[0]:
            price = self.data.close[-1]
            self.buy(size=0.1, sl=price - 0.01, tp=price + 0.01)
        elif df.signal_ema_crossunder[0]:
            price = self.data.close[-1]
            self.sell(size=0.1, sl=price + 0.01, tp=price - 0.01)

    def on_transaction(self, transaction):
        print("Transaction", transaction)

    def end(self):
        print(self.data)
        print(self.orders)

    def plot(self):
        import plotly.graph_objects as go

        df = self.data
        return [
            # EMA
            go.Scatter(
                x=df.index,
                y=df["ema1"],
                line=dict(color="blue", width=1),
                name="ema1",
            ),
            go.Scatter(
                x=df.index,
                y=df["ema2"],
                line=dict(color="green", width=1),
                name="ema2",
            ),
        ]


lt = LetTrade(
    strategy=SmaCross,
    datas="data/EURUSD=X_1h.csv",
)

lt.run()
lt.plot()
