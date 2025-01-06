from lettrade.all import DataFeed, ForexBackTestAccount, Strategy, let_backtest


class SmaCross(Strategy):
    ema1_window = 9
    ema2_window = 21

    def indicators(self, df: DataFeed):
        df.i.ema(name="ema1", window=self.ema1_window, inplace=True, plot=True)
        df.i.ema(name="ema2", window=self.ema2_window, inplace=True, plot=True)

        df.i.crossover("ema1", "ema2", inplace=True, plot=True)
        df.i.crossunder("ema1", "ema2", inplace=True, plot=True)

    def next(self, df: DataFeed):
        if df.l.crossover[-1] >= 100:
            self.exit_positions()
            self.buy(size=0.1)
        elif df.l.crossunder[-1] <= -100:
            self.exit_positions()
            self.sell(size=0.1)


if __name__ == "__main__":
    lt = let_backtest(
        strategy=SmaCross,
        datas="example/data/data/EURUSD_5m-0_1000.csv",
        account=ForexBackTestAccount,
    )

    lt.run()
    lt.plot()
