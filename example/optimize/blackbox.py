import blackbox as bb
import talib.abstract as ta

from lettrade import DataFeed, Strategy
from lettrade import indicator as i
from lettrade.exchange.backtest import ForexBackTestAccount, let_backtest


class SmaCross(Strategy):
    ema1_period = 9
    ema2_period = 21

    def indicators(self, df: DataFeed):
        df["ema1"] = ta.EMA(df, timeperiod=self.ema1_period)
        df["ema2"] = ta.EMA(df, timeperiod=self.ema2_period)

        df["signal_ema_crossover"] = i.crossover(df.ema1, df.ema2)
        df["signal_ema_crossunder"] = i.crossunder(df.ema1, df.ema2)

    def next(self, df: DataFeed):
        if len(self.orders) > 0 or len(self.positions) > 0:
            return

        if df.l.signal_ema_crossover[-1]:
            price = self.data.l.close[-1]
            self.buy(size=0.1, sl=price - 0.001, tp=price + 0.001)
        elif df.l.signal_ema_crossunder[-1]:
            price = self.data.l.close[-1]
            self.sell(size=0.1, sl=price + 0.001, tp=price - 0.001)


lt = let_backtest(
    strategy=SmaCross,
    datas="example/data/data/EURUSD_5m-0_10000.csv",
    account=ForexBackTestAccount,
)


def params_parser(args):
    return {"ema1_period": int(args[0]), "ema2_period": int(args[1])}


def result_parser(result):
    return -result["equity"]


result = bb.minimize(
    f=lt.optimize_model(
        params_parser=params_parser,
        result_parser=result_parser,
    ),
    domain=[[5, 25, 1], [10, 50, 1]],  # ranges of each parameter
    budget=300,  # total number of function calls available
    batch=12,  # number of calls that will be evaluated in parallel
)
lt.optimize_done()

lt.plotter.heatmap(x="ema1_period", y="ema2_period")
