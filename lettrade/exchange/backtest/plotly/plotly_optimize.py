import pandas as pd
import plotly.graph_objects as go
from plotly import express as px

from lettrade.plot.optimize import OptimizePlotter


class PlotlyOptimizePlotter(OptimizePlotter):
    _process_bar: "tqdm" = None

    def __init__(self, total=None, process_bar=True) -> None:
        super().__init__()

        self._total = total

        if process_bar:
            from tqdm import tqdm

            self._process_bar = tqdm(total=total)

    def on_result(self, result):
        if self._process_bar is not None:
            self._process_bar.update(1)

    def on_done(self):
        if self._process_bar is not None:
            self._process_bar.close()

    def load(self):
        raise NotImplementedError

    def plot(self, **kwargs):
        ids = []
        equities = []
        for result in self.results:
            ids.append(result[0])
            equities.append(result[2]["equity"])

        df = pd.DataFrame({"id": ids, "equity": equities})

        fig = px.scatter(df, x="id", y="equity")
        fig.show()

    def stop(self):
        raise NotImplementedError

    def _xyzs(self, x: str, y: str, z: str):
        xs = []
        ys = []
        zs = []
        for r in self.results:
            xs.append(r[1][x])
            ys.append(r[1][y])
            zs.append(r[2][z])

        return {x: xs, y: ys, z: zs}

    def heatmap(self, x: str, y: str, z: str = "equity", histfunc="max", **kwargs):
        df = pd.DataFrame(self._xyzs(x=x, y=y, z=z))
        fig = px.density_heatmap(
            df,
            x=x,
            y=y,
            z=z,
            nbinsx=int(df[x].max() - df[x].min()),
            nbinsy=int(df[y].max() - df[y].min()),
            histfunc=histfunc,
            color_continuous_scale="Viridis",
            **kwargs,
        )
        fig.show()

    def contour(self, x: str, y: str, z: str = "equity", histfunc="max", **kwargs):
        df = pd.DataFrame(self._xyzs(x=x, y=y, z=z))
        fig = px.density_contour(
            df,
            x=x,
            y=y,
            z=z,
            nbinsx=int(df[x].max() - df[x].min()),
            nbinsy=int(df[y].max() - df[y].min()),
            histfunc=histfunc,
            **kwargs,
        )
        fig.update_traces(contours_coloring="fill", contours_showlabels=True)
        fig.show()
