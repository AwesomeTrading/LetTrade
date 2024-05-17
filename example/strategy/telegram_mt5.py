import os

import pandas as pd
import talib.abstract as ta
from dotenv import load_dotenv

import example.logger
from lettrade import DataFeed, LetTrade, Strategy
from lettrade.commander import TelegramCommander
from lettrade.exchange.metatrader import MetaTrader
from lettrade.indicator import crossover, crossunder

load_dotenv()


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
        print("-" * 64, len(self.data))
        print(df)

        if len(self.orders) > 0 or len(self.trades) > 0:
            return

        # if len(self.data) >= 102:
        #     price = self.data.close[-1]
        #     result = self.buy(size=0.1, sl=price - 0.01, tp=price + 0.01)
        #     if not result.ok:
        #         print("[ERROR] ---> order:", result)

        if df.signal_ema_crossover[-1]:
            price = self.data.close[-1]
            self.buy(size=0.1, sl=price - 0.01, tp=price + 0.01)
        elif df.signal_ema_crossunder[-1]:
            price = self.data.close[-1]
            self.sell(size=0.1, sl=price + 0.01, tp=price - 0.01)

    # def on_transaction(self, transaction):
    #     print("Transaction", transaction)

    def end(self):
        print(self.data)
        print(self.orders)

    def plot(self, df: DataFeed):
        return [
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


if __name__ == "__main__":
    mt5 = MetaTrader(
        account=int(os.environ["MT5_LOGIN"]),
        password=os.environ["MT5_PASSWORD"],
        server=os.environ["MT5_SERVER"],
    )

    lt = LetTrade(
        strategy=SmaCross,
        datas=[mt5.data("EURGBP", "1m")],
        feeder=mt5.feeder(),
        exchange=mt5.exchange(),
        account=mt5.account(),
        commander=TelegramCommander(
            token=os.getenv("TELEGRAM_TOKEN"),
            chat_id=os.getenv("TELEGRAM_CHAT_ID"),
        ),
    )

    lt.run()
    # lt.plot()
