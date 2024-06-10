import queue
import threading
import time
from multiprocessing import Manager, Queue
from multiprocessing.managers import SyncManager
from typing import Optional

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from ..plot import OptimizePlotter


class PlotlyOptimizePlotter(OptimizePlotter):
    _total: int = 0
    _process_bar: "tqdm" = None
    _manager: SyncManager

    def __init__(self, total=None, process_bar=True) -> None:
        super().__init__()

        self._total = total

        if process_bar:
            from tqdm import tqdm

            self._process_bar = tqdm(total=total)

        self._t_wait_done()

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

            self._results.append(result)

            done += 1
            if self._process_bar is not None:
                self._process_bar.update(1)

            # Done
            if self._total > 0 and done == self._total:
                break

        self.done()

    def done(self):
        time.sleep(1)  # Wait for return finish
        if self._process_bar is not None:
            self._process_bar.close()
        self._manager.shutdown()

        print("optimize done", self._results)

    def load(self):
        raise NotImplementedError

    def plot(self, **kwargs):
        from plotly import express as px

        ids = []
        equities = []
        for result in self._results:
            ids.append(result[0])
            equities.append(result[2]["equity"])

        df = pd.DataFrame({"id": ids, "equity": equities})

        fig = px.scatter(df, x="id", y="equity")
        fig.show()

    def stop(self):
        raise NotImplementedError
