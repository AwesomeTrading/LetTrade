import logging
import os

import pandas as pd
from dotenv import load_dotenv

import example.logger
from lettrade import DataFeed, Strategy
from lettrade.exchange.ccxt import let_ccxt

load_dotenv()

logger = logging.getLogger(__name__)


class SmaCross(Strategy):
    ema1_window = 9
    ema2_window = 21
    _now: pd.Timestamp

    def indicators(self, df: DataFeed):
        df["ema1"] = df.i.ema(window=self.ema1_window)
        df["ema2"] = df.i.ema(window=self.ema2_window)

        df["signal_ema_crossover"] = df.i.crossover(df.ema1, df.ema2)
        df["signal_ema_crossunder"] = df.i.crossunder(df.ema1, df.ema2)

    def start(self, df: DataFeed):
        if self.is_live:
            self._now = df.now

    def next(self, df: DataFeed):
        if self.is_live:
            # Filter start of new bar
            if self._now == df.now:
                return

            self._now = df.now
            logger.info("New bar: %s", self._now)

        if len(self.orders) > 0 or len(self.positions) > 0:
            return

        if df.l.signal_ema_crossover[-1]:
            price = self.data.l.close[-1]
            self.buy(size=0.1, sl=price - 1000, tp=price + 1000)
        elif df.l.signal_ema_crossunder[-1]:
            price = self.data.l.close[-1]
            self.sell(size=0.1, sl=price + 1000, tp=price - 1000)

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
    lt = let_ccxt(
        strategy=SmaCross,
        datas=[("BTC/USD", "1m", "BTCUSD_1m")],
        ccxt_exchange=os.getenv("CCXT_EXCHANGE"),
        ccxt_type=os.getenv("CCXT_TYPE"),
        ccxt_key=os.getenv("CCXT_KEY"),
        ccxt_secret=os.getenv("CCXT_SECRET"),
        ccxt_verbose=os.getenv("CCXT_VERBOSE", "").lower() in ["true", "1"],
    )

    lt.run()
    # lt.plot()
