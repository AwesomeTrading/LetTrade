from lettrade.plot.plot import Plotter


class OptimizePlotter(Plotter):
    """
    Class help to plot `lettrade`
    """

    results: list

    def __init__(self) -> None:
        super().__init__()

    def init(self, results: list):
        self.results = results

    def on_result(self, result):
        """"""

    def on_done(self):
        """"""

    def heatmap(self, x: str, y: str, z: str = "equity", **kwargs):
        """"""

    def contour(self, x: str, y: str, z: str = "equity", **kwargs):
        """"""
