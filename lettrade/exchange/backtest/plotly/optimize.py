from typing import TYPE_CHECKING

import pandas as pd

# import plotly.graph_objects as go
from plotly import express as px

from ..plot import OptimizePlotter

if TYPE_CHECKING:
    from rich.progress import Progress


class PlotlyOptimizePlotter(OptimizePlotter):
    _process_bar: "Progress | None"

    def __init__(self, total=None, process_bar: bool = True) -> None:
        super().__init__()

        self._total = total

        if process_bar:
            from rich.progress import (
                BarColumn,
                Console,
                Progress,
                SpinnerColumn,
                TaskProgressColumn,
                TextColumn,
                TimeElapsedColumn,
                TimeRemainingColumn,
            )

            console = Console(record=True, force_jupyter=False)
            self._process_bar = Progress(
                SpinnerColumn(),
                # *Progress.get_default_columns(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                TextColumn("[bold blue][{task.completed}/{task.total}]"),
                TimeRemainingColumn(),
                TimeElapsedColumn(),
                console=console,
                # transient=False,
            )
            self._process_bar.add_task("[cyan2]Optimizing", total=total)
            self._process_bar.start()
        else:
            self._process_bar = None

    def on_result(self, result):
        if self._process_bar is not None:
            task_id = next(iter(self._process_bar._tasks))
            self._process_bar.update(
                task_id,
                advance=1,
                refresh=True,
            )

    def on_done(self):
        if self._process_bar is not None:
            # self._process_bar.refresh()
            self._process_bar.stop()

    def load(self):
        raise NotImplementedError

    def plot(self, **kwargs):
        """Plot optimize result"""
        ids = []
        equities = []
        for result in self.results:
            ids.append(result["index"])
            equities.append(result["result"]["equity"])

        df = pd.DataFrame({"id": ids, "equity": equities})

        fig = px.scatter(df, x="id", y="equity")
        fig.show()

    def stop(self):
        raise NotImplementedError

    def _xyzs(self, x: str, y: str, z: str):
        xs = []
        ys = []
        zs = []
        for result in self.results:
            xs.append(result["optimize"][x])
            ys.append(result["optimize"][y])
            zs.append(result["result"][z])

        return {x: xs, y: ys, z: zs}

    def _xyz_default(self, x, y, z):
        if x is None or y is None:
            if len(self.results) == 0:
                raise RuntimeError("Result is empty")

            optimize_keys = list(self.results[0]["optimize"].keys())
            if x is None:
                x = optimize_keys[0]
            if y is None:
                y = optimize_keys[1]
        if z is None:
            z = "equity"
        return x, y, z

    def heatmap(
        self,
        x: str = None,
        y: str = None,
        z: str = "equity",
        histfunc="max",
        **kwargs,
    ):
        """Plot optimize heatmap

        Args:
            x (str, optional): _description_. Defaults to None.
            y (str, optional): _description_. Defaults to None.
            z (str, optional): _description_. Defaults to "equity".
            histfunc (str, optional): _description_. Defaults to "max".
        """
        x, y, z = self._xyz_default(x, y, z)
        df = pd.DataFrame(self._xyzs(x=x, y=y, z=z))
        fig = px.density_heatmap(
            df,
            x=x,
            y=y,
            z=z,
            nbinsx=int(df[x].max() - df[x].min() + 1),
            nbinsy=int(df[y].max() - df[y].min() + 1),
            histfunc=histfunc,
            color_continuous_scale="Viridis",
            **kwargs,
        )
        fig.show()

    def contour(
        self,
        x: str = None,
        y: str = None,
        z: str = "equity",
        histfunc="max",
        **kwargs,
    ):
        """Plot optimize contour

        Args:
            x (str, optional): _description_. Defaults to None.
            y (str, optional): _description_. Defaults to None.
            z (str, optional): _description_. Defaults to "equity".
            histfunc (str, optional): _description_. Defaults to "max".
        """
        x, y, z = self._xyz_default(x, y, z)
        df = pd.DataFrame(self._xyzs(x=x, y=y, z=z))
        fig = px.density_contour(
            df,
            x=x,
            y=y,
            z=z,
            nbinsx=int(df[x].max() - df[x].min() + 1),
            nbinsy=int(df[y].max() - df[y].min() + 1),
            histfunc=histfunc,
            **kwargs,
        )
        fig.update_traces(contours_coloring="fill", contours_showlabels=True)
        fig.show()
