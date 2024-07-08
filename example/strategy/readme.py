import talib.abstract as ta

from lettrade import indicator as i
from lettrade.all import DataFeed, ForexBackTestAccount, Strategy, let_backtest


class SmaCross(Strategy):
    ema1_window = 9
    ema2_window = 21

    def indicators(self, df: DataFeed):
        df["ema1"] = ta.EMA(df, timeperiod=self.ema1_window)
        df.i.ema(name="ema2", window=self.ema2_window, inplace=True, plot=True)

        df["crossover"] = i.crossover(df.ema1, df.ema2)
        df.i.crossunder("ema1", "ema2", inplace=True, plot=True)

    def next(self, df: DataFeed):
        if df.l.crossover[-1]:
            self.positions_exit()
            self.buy(size=0.1)
        elif df.l.crossunder[-1]:
            self.positions_exit()
            self.sell(size=0.1)

    def plot(self, config: dict, df: DataFeed) -> dict:
        from lettrade.plot.plotly import PlotColor, plot_line, plot_mark, plot_merge

        plot_ema1 = plot_line(df["ema1"], dataframe=df, color="green")
        plot_crossover = plot_mark(
            df["close"],
            filter=df["crossover"] >= 100,
            dataframe=df,
            name="crossover",
            color=PlotColor.BLUE,
        )
        return plot_merge(config, plot_ema1, plot_crossover)


if __name__ == "__main__":
    lt = let_backtest(
        strategy=SmaCross,
        datas="example/data/data/EURUSD_5m-0_1000.csv",
        account=ForexBackTestAccount,
    )

    lt.run()
    lt.plot()
