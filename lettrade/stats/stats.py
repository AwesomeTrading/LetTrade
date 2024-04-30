import logging

import numpy as np
import pandas as pd

from ..data import DataFeeder
from ..exchange import Exchange
from ..strategy import Strategy

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

        self.result = pd.Series(dtype=object)

    def compute(self):
        data: pd.DataFrame = self.feeder.data

        self.result.loc["Start"] = data.datetime.iloc[0]
        self.result.loc["End"] = data.datetime.iloc[-1]

        # self.result.loc["Start"] = data.datetime.iloc[0].astype("datetime64[ns]")
        # self.result.loc["End"] = data.datetime.iloc[-1].astype("datetime64[ns]")
        self.result.loc["Duration"] = self.result.End - self.result.Start

        return self.result

    def show(self):
        if "Start" not in self.result:
            logger.warning("call compute() before show()")
            self.compute()

        print("=" * 64)
        print(self.result)
