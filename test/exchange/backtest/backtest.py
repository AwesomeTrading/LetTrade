import pytest
import talib.abstract as ta

from lettrade import DataFeed, Strategy
from lettrade import indicator as i
from lettrade.exchange.backtest import (
    ForexBackTestAccount,
    LetTradeBackTest,
    let_backtest,
)


class BackTestStrategy(Strategy):
    ema1_period = 9
    ema2_period = 21

    def indicators(self, df: DataFeed):
        df["ema1"] = ta.EMA(df, timeperiod=self.ema1_period)
        df["ema2"] = ta.EMA(df, timeperiod=self.ema2_period)
        # df["ema1"] = df.close.ema(window=self.ema1_period)
        # df["ema2"] = df.close.ema(window=self.ema2_period)

        df["signal_ema_crossover"] = i.crossover(df.ema1, df.ema2)
        df["signal_ema_crossunder"] = i.crossunder(df.ema1, df.ema2)

    def next(self, df: DataFeed):
        if len(self.orders) > 0 or len(self.positions) > 0:
            return

        if df.l.signal_ema_crossover[-1]:
            price = df.l.close[-1]
            self.buy(size=0.1, sl=price - 0.001, tp=price + 0.001)
        elif df.l.signal_ema_crossunder[-1]:
            price = df.l.close[-1]
            self.sell(size=0.1, sl=price + 0.001, tp=price - 0.001)


@pytest.fixture
def lt():
    lt = let_backtest(
        strategy=BackTestStrategy,
        datas="example/data/data/EURUSD_5m_0_1000.csv",
        account=ForexBackTestAccount,
    )

    return lt


def test_run(lt: LetTradeBackTest):
    lt.run()
    result = lt.stats.result
    assert result.positions == 15
