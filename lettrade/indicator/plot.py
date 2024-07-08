from typing import Callable

import pandas as pd

DATAFRAME_PLOTTERS_NAME = "_lt_plotters"


class IndicatorPlotter:
    """Add indicator plotter to DataFrame"""

    def __init__(
        self,
        dataframe: pd.DataFrame,
        plotter: Callable,
        filter: Callable | pd.Series | None = None,
        push: bool = True,
        **kwargs,
    ) -> None:
        # self.dataframe: pd.DataFrame = dataframe
        self.plotter: Callable = plotter
        self.filter: Callable | pd.Series | None = filter
        self.kwargs = kwargs

        if push:
            indicator_push_plotter(dataframe=dataframe, ip=self)

    def config(self, dataframe: pd.DataFrame):
        df_name = dataframe.name
        if self.filter is not None:
            if callable(self.filter):
                filter = self.filter(dataframe)
            else:
                filter = self.filter

            self.kwargs.update(filter=filter)

        config = self.plotter(dataframe=dataframe, **self.kwargs)

        if df_name in config:
            return config

        return {f"{df_name}": config}


def indicator_push_plotter(dataframe: pd.DataFrame, ip: IndicatorPlotter):
    if not hasattr(dataframe, DATAFRAME_PLOTTERS_NAME):
        object.__setattr__(dataframe, DATAFRAME_PLOTTERS_NAME, [])

    getattr(dataframe, DATAFRAME_PLOTTERS_NAME).append(ip)


def indicator_load_plotters(dataframe: pd.DataFrame) -> dict:
    if not hasattr(dataframe, DATAFRAME_PLOTTERS_NAME):
        return dict()

    from lettrade.plot.plotly import plot_merge

    config = dict()
    for plotter in getattr(dataframe, DATAFRAME_PLOTTERS_NAME):
        plot_merge(config, plotter.config(dataframe=dataframe))

    return config
