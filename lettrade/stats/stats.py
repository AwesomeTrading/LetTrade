import logging

import numpy as np
import pandas as pd

from lettrade.account import Account
from lettrade.data import DataFeeder
from lettrade.exchange import Exchange
from lettrade.strategy import Strategy

logger = logging.getLogger(__name__)


class Statistic:
    """
    Compute strategy result
    """

    result: pd.Series

    def __init__(
        self,
        feeder: DataFeeder,
        exchange: Exchange,
        strategy: Strategy,
    ) -> None:
        self.feeder: DataFeeder = feeder
        self.exchange: Exchange = exchange
        self.strategy: Strategy = strategy
        self.account: Account = strategy.account

    def compute(self):
        """
        Calculate strategy report
        """
        data: pd.DataFrame = self.feeder.data
        self.result = pd.Series(dtype=object)

        self.result.loc["# Strategy"] = self.strategy.__class__
        self.result.loc["Start"] = data.datetime.iloc[0]
        self.result.loc["End"] = data.datetime.iloc[-1]
        self.result.loc["Duration"] = self.result.End - self.result.Start

        # Equity
        equities = list(self.account._equities.values())
        self.result.loc["Start Balance [$]"] = round(equities[0], 2)
        self.result.loc["Equity [$]"] = round(equities[-1], 2)

        pl = equities[-1] - equities[0]
        self.result.loc["PL [$]"] = round(pl, 2)
        self.result.loc["PL [%]"] = round(pl / equities[0] * 100, 2)

        # TODO
        self.result.loc["Buy & Hold PL [%]"] = 2.0
        self.result.loc["Max. Drawdown [%]"] = -33.08
        self.result.loc["Avg. Drawdown [%]"] = -5.58
        self.result.loc["Max. Drawdown Duration"] = "688 days 00:00:00"
        self.result.loc["Avg. Drawdown Duration"] = "41 days 00:00:00"

        # Separator
        self.result.loc[""] = ""

        # Trades
        trades = list(self.exchange.history_trades.values()) + list(
            self.exchange.trades.values()
        )
        self.result.loc["# Trades"] = len(trades)
        self.result.loc["Best Trade [%]"] = max(t.pl for t in trades)
        self.result.loc["Worst Trade [%]"] = min(t.pl for t in trades)

        # TODO
        self.result.loc["Profit Factor"] = 2.13
        self.result.loc["SQN"] = 1.78

        return self.result

    def show(self):
        """
        Show statistic report
        """
        if "Start" not in self.result:
            logger.warning("call compute() before show()")
            self.compute()

        # Show result inside docs session
        if __debug__:
            show = self._docs_show()
            if show:
                print(show)
                return show

        logger.info(
            "\n============= Statistic result =============\n%s\n",
            self.result.to_string(),
        )

    def _docs_show(self):
        if __debug__:
            from ..utils.docs import is_docs_session

            if not is_docs_session():
                return False

            return self.result.to_string()
