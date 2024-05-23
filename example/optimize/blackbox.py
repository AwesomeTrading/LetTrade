# pip install black-box
import black_box as bb
import talib.abstract as ta

from lettrade import DataFeed, Strategy, crossover, crossunder
from lettrade.exchange.backtest import ForexBackTestAccount, let_backtest


class SmaCross(Strategy):
    ema1_period = 9
    ema2_period = 21

    def indicators(self, df: DataFeed):
        df["ema1"] = ta.EMA(df, timeperiod=self.ema1_period)
        df["ema2"] = ta.EMA(df, timeperiod=self.ema2_period)

        df["signal_ema_crossover"] = crossover(df.ema1, df.ema2)
        df["signal_ema_crossunder"] = crossunder(df.ema1, df.ema2)

    def next(self, df: DataFeed):
        if len(self.orders) > 0 or len(self.trades) > 0:
            return

        if df.signal_ema_crossover[-1]:
            price = self.data.close[-1]
            self.buy(size=0.1, sl=price - 0.01, tp=price + 0.01)
        elif df.signal_ema_crossunder[-1]:
            price = self.data.close[-1]
            self.sell(size=0.1, sl=price + 0.01, tp=price - 0.01)

    # def on_transaction(self, transaction):
    #     print("Transaction", transaction)

    # def end(self, df: DataFeed):
    #     print(df.tail())
    #     print(self.orders)

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


lt = let_backtest(
    strategy=SmaCross,
    datas=["example/data/data/EURUSD_5m_0_1000.csv"],
    account=ForexBackTestAccount,
)


def args_parser(args):
    return [
        ("ema1_period", int(args[0])),
        ("ema2_period", int(args[1])),
    ]


def result_parser(result):
    return result["Equity [$]"]


best_params = bb.search_min(
    f=lt.optimize_instance(
        args_parser=args_parser,
        result_parser=result_parser,
    ),  # given function
    domain=[[5, 15], [10, 30]],  # ranges of each parameter
    budget=40,  # total number of function calls available
    batch=1,  # number of calls that will be evaluated in parallel
    resfile="output.csv",
)  # text file where results will be saved
