from multiprocessing import Queue

from lettrade.plot import Plotter


class OptimizePlotter(Plotter):
    """
    Class help to plot `lettrade`
    """

    _q: Queue
    _results: list

    def __init__(self) -> None:
        super().__init__()
        self._results = []

    def heatmap(self):
        """"""

    @property
    def queue(self) -> Queue:
        return self._q
