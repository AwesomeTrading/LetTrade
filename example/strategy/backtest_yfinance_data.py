import pandas_ta as pta

import example.logger
from lettrade.all import DataFeed, Strategy, YFBackTestDataFeed, let_backtest


class SmaCross(Strategy):
    ema1_window = 9
    ema2_window = 21

    def indicators(self, df: DataFeed):
        # EMA
        df.i.ema(window=self.ema1_window, name="ema1", inplace=True, plot=True)
        df.i.ema(window=self.ema2_window, name="ema2", inplace=True, plot=True)

        df.i.crossover(
            "ema1",
            "ema2",
            name="signal_ema_crossover",
            inplace=True,
            plot=True,
        )
        df.i.crossunder(
            "ema1",
            "ema2",
            name="signal_ema_crossunder",
            inplace=True,
            plot=True,
        )

        # BBands
        df.i.bollinger_bands(window=20, std=2.0, inplace=True, plot=True)

        return df

    def next(self, df: DataFeed):
        if df.l.signal_ema_crossover[-1]:
            self.buy(size=0.1)
        elif df.l.signal_ema_crossunder[-1]:
            self.sell(size=0.1)

    def stop(self, df: DataFeed):
        print(df.tail())


if __name__ == "__main__":
    lt = let_backtest(
        strategy=SmaCross,
        datas=[
            YFBackTestDataFeed(
                name="EURUSD",
                ticker="EURUSD=X",
                since="2023-01-01",
                to="2023-02-01",
                interval="1h",
            )
        ],
    )

    lt.run()
    lt.plot()
