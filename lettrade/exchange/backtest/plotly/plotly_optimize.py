import pandas as pd
import plotly.graph_objects as go
from plotly import express as px
from plotly.subplots import make_subplots

from ..plot import OptimizePlotter


class PlotlyOptimizePlotter(OptimizePlotter):
    _process_bar: "tqdm" = None
    _results: list

    def __init__(self, total=None, process_bar=True) -> None:
        super().__init__()

        self._total = total
        self._results = []
        if process_bar:
            from tqdm import tqdm

            self._process_bar = tqdm(total=total)

    def on_result(self, result):
        if self._process_bar is not None:
            self._process_bar.update(1)

    def on_done(self, results):
        self._results = results

        if self._process_bar is not None:
            self._process_bar.close()

    def load(self):
        raise NotImplementedError

    def plot(self, **kwargs):
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
