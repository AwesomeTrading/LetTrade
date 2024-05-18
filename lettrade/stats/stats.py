import logging

import numpy as np
import pandas as pd

from lettrade.account import Account
from lettrade.data import DataFeeder
from lettrade.exchange import Exchange
from lettrade.strategy import Strategy

logger = logging.getLogger(__name__)


class Statistic:
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

        self.result = pd.Series(dtype=object)

    def compute(self):
        data: pd.DataFrame = self.feeder.data

        self.result.loc["Start"] = data.datetime.iloc[0]
        self.result.loc["End"] = data.datetime.iloc[-1]

        # self.result.loc["Start"] = data.datetime.iloc[0].astype("datetime64[ns]")
        # self.result.loc["End"] = data.datetime.iloc[-1].astype("datetime64[ns]")
        self.result.loc["Duration"] = self.result.End - self.result.Start

        equities = list(self.account._equities.values())
        self.result.loc["PnL"] = round(equities[-1] - equities[0], 2)
        self.result.loc["PnL (%)"] = "%.2f %%" % (self.result.PnL / equities[0] * 100)

        return self.result

    def show(self):
        if "Start" not in self.result:
            logger.warning("call compute() before show()")
            self.compute()

        logger.info("\n========== Statistic result ==========\n%s", self.result)
