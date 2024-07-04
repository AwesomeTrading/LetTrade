from lettrade import DataFeed, Strategy
from lettrade.exchange.backtest import ForexBackTestAccount, let_backtest


class SmaCross(Strategy):
    ema1_window = 9
    ema2_window = 21

    def indicators(self, df: DataFeed):
        df["ema1"] = df.i.ema(window=self.ema1_window)
        df["ema2"] = df.i.ema(window=self.ema2_window)

        df["signal_ema_crossover"] = df.i.crossover(df.ema1, df.ema2)
        df["signal_ema_crossunder"] = df.i.crossunder(df.ema1, df.ema2)

    def next(self, df: DataFeed):
        if len(self.orders) > 0 or len(self.positions) > 0:
            return

        if df.l.signal_ema_crossover[-1]:
            price = df.l.close[-1]
            self.buy(size=0.1, sl=price - 0.001, tp=price + 0.001)
        elif df.l.signal_ema_crossunder[-1]:
            price = df.l.close[-1]
            self.sell(size=0.1, sl=price + 0.001, tp=price - 0.001)


if __name__ == "__main__":
    lt = let_backtest(
        strategy=SmaCross,
        datas="example/data/data/EURUSD_5m-0_10000.csv",
        account=ForexBackTestAccount,
    )

    # lt.run()
    lt.optimize(
        ema1_window=range(5, 50),
        ema2_window=range(5, 50),
        # multiprocessing=None,
        # workers=1,
        # cache=None,
    )

    lt.plot()
    lt.plotter.heatmap()
    lt.plotter.contour()
