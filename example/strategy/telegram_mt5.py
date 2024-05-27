import os

import talib.abstract as ta
from dotenv import load_dotenv

import example.logger
from lettrade.all import (
    DataFeed,
    Strategy,
    TelegramCommander,
    crossover,
    crossunder,
    let_metatrader,
)

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

    def end(self, df: DataFeed):
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


if __name__ == "__main__":
    lt = let_metatrader(
        strategy=SmaCross,
        datas=[[("EURGBP", "1m")]],
        login=int(os.environ["MT5_LOGIN"]),
        password=os.environ["MT5_PASSWORD"],
        server=os.environ["MT5_SERVER"],
        commander=TelegramCommander,
        commander_kwargs=dict(
            token=os.getenv("TELEGRAM_TOKEN"),
            chat_id=os.getenv("TELEGRAM_CHAT_ID"),
        ),
        wine=os.getenv("MT5_WINE", None),
    )

    lt.run()
    # lt.plot()
