import os

import talib.abstract as ta
from dotenv import load_dotenv

import example.logger
from lettrade import DataFeed, Strategy
from lettrade.exchange.metatrader import let_metatrader

load_dotenv()


class SmaCross(Strategy):
    ema1_window = 9
    ema2_window = 21

    def indicators(self, df: DataFeed):
        df["ema1"] = ta.EMA(df, timewindow=self.ema1_window)
        df["ema2"] = ta.EMA(df, timewindow=self.ema2_window)

        df["signal_ema_crossover"] = df.i.crossover(df.ema1, df.ema2)
        df["signal_ema_crossunder"] = df.i.crossunder(df.ema1, df.ema2)
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

    def stop(self, df: DataFeed):
        print(df)
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


if __name__ == "__main__":
    lt = let_metatrader(
        strategy=SmaCross,
        datas=[("EURUSD", "1m")],
        # datas=[[("EURUSD", "1m")], [("GBPUSD", "1m")]],
        mt5_login=int(os.environ["MT5_LOGIN"]),
        mt5_password=os.environ["MT5_PASSWORD"],
        mt5_server=os.environ["MT5_SERVER"],
        mt5_wine=os.getenv("MT5_WINE", None),
    )

    lt.run()
    # lt.plot()
