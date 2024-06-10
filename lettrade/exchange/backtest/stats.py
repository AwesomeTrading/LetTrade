import logging
import queue
import threading
from multiprocessing import Manager, Queue
from multiprocessing.managers import SyncManager

import pandas as pd

from .plot import OptimizePlotter

logger = logging.getLogger(__name__)


class OptimizeStatistic:
    """
    Compute strategy result
    """

    _q: Queue
    _total: int = 0
    _manager: SyncManager

    results: list
    result: pd.Series
    plotter: OptimizePlotter = None

    def __init__(self, plotter: OptimizePlotter = None, total: int = 0) -> None:
        self.plotter = plotter
        self.results = []
        self._total = total

        self._t_wait_done()

    @property
    def queue(self) -> Queue:
        return self._q

    def _t_wait_done(self):
        self._manager = Manager()
        self._q = self._manager.Queue(maxsize=1_000)
        t = threading.Thread(target=self._wait_done)
        t.start()

    def _wait_done(self):
        done = 0
        while True:
            try:
                result = self._q.get(timeout=3)
            except queue.Empty:
                # TODO: check closed main class then exit
                continue

            # Done
            if result is None:
                break

            self.results.append(result)

            done += 1

            if self.plotter:
                self.plotter.on_result(result)

            # Done
            if self._total > 0 and done == self._total:
                break

        self.done()

    def done(self):
        if self.plotter:
            self.plotter.on_done(self.results)
        self._manager.shutdown()

        print("Stats done", self.results)

    def compute(self):
        """
        Calculate strategy report
        """

        return self.result

    def __repr__(self) -> str:
        self.result = self.result.rename(
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
        return str(self.result.to_string())

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
