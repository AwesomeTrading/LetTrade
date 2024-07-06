from typing import Callable

import pandas as pd

DATAFRAME_PLOTTERS_NAME = "_lt_plotters"


def indicator_add_plotter(dataframe: pd.DataFrame, plotter: Callable, **kwargs):
    def _indicator_plot(dataframe: pd.DataFrame) -> dict:
        config = plotter(dataframe=dataframe, **kwargs)

        if dataframe.name in config:
            return config

        return {f"{dataframe.name}": config}

    if not hasattr(dataframe, DATAFRAME_PLOTTERS_NAME):
        object.__setattr__(dataframe, DATAFRAME_PLOTTERS_NAME, [])

    getattr(dataframe, DATAFRAME_PLOTTERS_NAME).append(_indicator_plot)


def indicator_load_plotters(dataframe: pd.DataFrame) -> dict:
    if not hasattr(dataframe, DATAFRAME_PLOTTERS_NAME):
        return dict()

    from lettrade.plot.plotly import plot_merge

    config = dict()
    for plotter in getattr(dataframe, DATAFRAME_PLOTTERS_NAME):
        plot_merge(config, plotter(dataframe=dataframe))

    return config
