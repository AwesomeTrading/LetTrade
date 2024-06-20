import logging
import queue
import threading
import time
from multiprocessing import Manager, Queue
from multiprocessing.managers import SyncManager

import pandas as pd

from lettrade.plot import OptimizePlotter

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

        if self.plotter is not None:
            self.plotter.init(self.results)

        self._t_wait_done()

    @property
    def queue(self) -> Queue:
        return self._q

    def _t_wait_done(self):
        self._manager = Manager()
        self._q = self._manager.Queue(maxsize=1_000)
        t = threading.Thread(target=self._wait_done)
        t.start()

    def _wait_done(self, retry=10):
        done = 0
        while True:
            try:
                result = self._q.get(timeout=3)
            except queue.Empty:
                continue
            except (AttributeError, BrokenPipeError):
                break
            except Exception as e:
                # TODO: check closed main class then exit
                retry -= 1
                if retry <= 0:
                    logger.warning("queue %s", e, exc_info=e)
                    break
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
            self.plotter.on_done()

        time.sleep(1)  # Wait for return finish

        if self._manager is not None:
            self._manager.shutdown()
            del self._manager
            self._manager = None

        if self._q is not None:
            try:
                self._q.close()
                del self._q
            except Exception:
                pass
            self._q = None

    def compute(self):
        """
        Calculate strategy report
        """

        return self.result

    def stop(self):
        self.done()
