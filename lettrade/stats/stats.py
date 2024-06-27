import logging

import numpy as np
import pandas as pd

from lettrade.account import Account
from lettrade.data import DataFeeder, TimeFrame
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
        """Calculate strategy report"""
        data = self.feeder.data

        ### Stats
        self.result = result = pd.Series(dtype=object)

        result.loc["strategy"] = str(self.strategy.__class__)
        result.loc["start"] = data.index[0]
        result.loc["end"] = data.index[-1]
        result.loc["duration"] = result.end - result.start

        ### Equity
        equities_index = pd.DatetimeIndex(self.account._equities.keys())
        equities = pd.Series(self.account._equities.values(), index=equities_index)
        dd = 1 - equities / np.maximum.accumulate(equities)
        dd_dur, dd_peaks = _compute_drawdown_duration_peaks(
            pd.Series(dd, index=equities_index)
        )

        result.loc["start_balance"] = round(equities.iloc[0], 2)
        result.loc["equity"] = round(equities.iloc[-1], 2)
        result.loc["equity_peak"] = round(equities.max(), 2)

        pl = equities.iloc[-1] - equities.iloc[0]
        result.loc["pl"] = round(pl, 2)
        result.loc["pl_percent"] = round(pl / equities.iloc[0] * 100, 2)

        c = data.close.values
        result.loc["buy_hold_pl_percent"] = round(
            (c[-1] - c[0]) / c[0] * 100, 2
        )  # long-only return

        max_dd = -np.nan_to_num(dd.max())
        result.loc["max_drawdown_percent"] = round(max_dd * 100, 2)
        result.loc["avg_drawdown_percent"] = round(-dd_peaks.mean() * 100, 2)
        result.loc["max_drawdown_duration"] = _round_timedelta(
            dd_dur.max(), data.timeframe
        )
        result.loc["avg_drawdown_duration"] = _round_timedelta(
            dd_dur.mean(), data.timeframe
        )

        # Separator
        result.loc[""] = ""

        ### Positions
        positions = list(self.exchange.history_positions.values()) + list(
            self.exchange.positions.values()
        )
        positions_columns = (
            "size",
            "entry_at",
            "exit_at",
            "entry_price",
            "exit_price",
            "pl",
            "fee",
        )
        positions_df = pd.DataFrame(columns=positions_columns)
        for position in positions:
            positions_df.at[position.id, positions_columns] = (
                position.size,
                position.entry_at,
                position.exit_at,
                position.entry_price,
                position.exit_price,
                position.pl,
                position.fee,
            )
        positions_df["duration"] = positions_df["entry_at"] - positions_df["exit_at"]
        positions_total = len(positions)
        pl = positions_df["pl"]

        result.loc["positions"] = positions_total

        win_rate = np.nan if not positions_total else (pl > 0).mean()
        result.loc["win_rate"] = round(win_rate, 2)
        result.loc["fee"] = round(positions_df.fee.sum(), 2)
        result.loc["best_trade_percent"] = round(pl.max(), 2)
        result.loc["worst_trade_percent"] = round(pl.min(), 2)
        result.loc["sqn"] = round(
            np.sqrt(positions_total) * pl.mean() / (pl.std() or np.nan),
            2,
        )
        result.loc["kelly_criterion"] = win_rate - (1 - win_rate) / (
            pl[pl > 0].mean() / -pl[pl < 0].mean()
        )
        result.loc["profit_factor"] = pl[pl > 0].sum() / (
            abs(pl[pl < 0].sum()) or np.nan
        )

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
                "equity_peak": "Equity Peak [$]",
                "pl": "PL [$]",
                "pl_percent": "PL [%]",
                "buy_hold_pl_percent": "Buy & Hold PL [%]",
                "max_drawdown_percent": "Max. Drawdown [%]",
                "avg_drawdown_percent": "Avg. Drawdown [%]",
                "max_drawdown_duration": "Max. Drawdown Duration",
                "avg_drawdown_duration": "Avg. Drawdown Duration",
                "positions": "# Positions",
                "win_rate": "Win Rate [%]",
                "fee": "Fee [$]",
                "best_trade_percent": "Best Trade [%]",
                "worst_trade_percent": "Worst Trade [%]",
                "profit_factor": "Profit Factor",
                "kelly_criterion": "Kelly Criterion",
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


def _round_timedelta(value, timeframe: TimeFrame):
    if not isinstance(value, pd.Timedelta):
        return value
    return timeframe.ceil(value)


def _compute_drawdown_duration_peaks(dd: pd.Series):
    # TODO: clean
    iloc = np.unique(np.r_[(dd == 0).values.nonzero()[0], len(dd) - 1])
    iloc = pd.Series(iloc, index=dd.index[iloc])
    df = iloc.to_frame("iloc").assign(prev=iloc.shift())
    df = df[df["iloc"] > df["prev"] + 1].astype(int)

    # If no drawdown since no trade, avoid below for pandas sake and return nan series
    if not len(df):
        return (dd.replace(0, np.nan),) * 2

    df["duration"] = df["iloc"].map(dd.index.__getitem__) - df["prev"].map(
        dd.index.__getitem__
    )
    df["peak_dd"] = df.apply(
        lambda row: dd.iloc[row["prev"] : row["iloc"] + 1].max(), axis=1
    )
    df = df.reindex(dd.index)
    return df["duration"], df["peak_dd"]
