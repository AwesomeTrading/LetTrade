import logging

import numpy as np
import pandas as pd

from lettrade.account import Account
from lettrade.data import DataFeeder
from lettrade.exchange import Exchange
from lettrade.strategy import Strategy

logger = logging.getLogger(__name__)


class BotStatistic:
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

    def stop(self):
        pass

    def compute(self):
        """
        Calculate strategy report
        """
        data = self.feeder.data

        equities = list(self.account._equities.values())
        trades = list(self.exchange.history_trades.values()) + list(
            self.exchange.trades.values()
        )

        self.result = pd.Series(dtype=object)

        self.result.loc["strategy"] = str(self.strategy.__class__)
        self.result.loc["start"] = data.index[0]
        self.result.loc["end"] = data.index[-1]
        self.result.loc["duration"] = self.result.end - self.result.start

        # Equity
        self.result.loc["start_balance"] = round(equities[0], 2)
        self.result.loc["equity"] = round(equities[-1], 2)

        pl = equities[-1] - equities[0]
        self.result.loc["pl"] = round(pl, 2)
        self.result.loc["pl_percent"] = round(pl / equities[0] * 100, 2)

        # TODO
        self.result.loc["buy_hold_pl_percent"] = 2.0
        self.result.loc["max_drawdown_percent"] = -33.08
        self.result.loc["avg_drawdown_percent"] = -5.58
        self.result.loc["max_drawdown_duration"] = "688 days 00:00:00"
        self.result.loc["avg_drawdown_duration"] = "41 days 00:00:00"

        # Separator
        self.result.loc[""] = ""

        # Trades
        self.result.loc["trades"] = len(trades)
        if trades:
            win_count = sum(1 for t in trades if t.pl > 0)
            win_rate = win_count / len(trades) * 100
        else:
            win_rate = 0

        self.result.loc["win_rate"] = round(win_rate, 2)
        self.result.loc["fee"] = sum(t.fee for t in trades) if trades else 0
        self.result.loc["best_trade_percent"] = (
            max(t.pl for t in trades) if trades else 0
        )
        self.result.loc["worst_trade_percent"] = (
            min(t.pl for t in trades) if trades else 0
        )

        # TODO
        self.result.loc["profit_factor"] = 2.13
        self.result.loc["sqn"] = 1.78

        return self.result

    def __repr__(self) -> str:
        result = self.result.rename(
            {
                "strategy": "# Strategy",
                "start": "Start",
                "end": "End",
                "duration": "Duration",
                "start_balance": "Start Balance",
                "equity": "Equity [$]",
                "pl": "PL [$]",
                "pl_percent": "PL [%]",
                "buy_hold_pl_percent": "Buy & Hold PL [%]",
                "max_drawdown_percent": "Max. Drawdown [%]",
                "avg_drawdown_percent": "Avg. Drawdown [%]",
                "max_drawdown_duration": "Max. Drawdown Duration",
                "avg_drawdown_duration": "Avg. Drawdown Duration",
                "trades": "# Trades",
                "win_rate": "Win Rate [%]",
                "fee": "Fee [$]",
                "best_trade_percent": "Best Trade [%]",
                "worst_trade_percent": "Worst Trade [%]",
                "profit_factor": "Profit Factor",
                "sqn": "SQN",
            }
        )
        return str(result.to_string())

    def show(self):
        """
        Show statistic report
        """
        if "Start" not in self.result:
            logger.warning("call compute() before show()")
            self.compute()

        # Show result inside docs session
        if __debug__:
            from lettrade.utils.docs import is_docs_session

            if is_docs_session():
                print(str(self))
                return

        logger.info(
            "\n============= Statistic result =============\n%s\n",
            str(self),
        )
