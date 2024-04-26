from numbers import Number
from typing import Callable, Optional, Sequence, Union

import pandas as pd


def crossover(series1: Sequence, series2: Sequence) -> bool:
    """
    Return `True` if `series1` just crossed over (above)
    `series2`.

        >>> crossover(self.data.Close, self.sma)
        True
    """
    series1 = (
        series1.values
        if isinstance(series1, pd.Series)
        else (series1, series1) if isinstance(series1, Number) else series1
    )
    series2 = (
        series2.values
        if isinstance(series2, pd.Series)
        else (series2, series2) if isinstance(series2, Number) else series2
    )
    try:
        return series1[-2] < series2[-2] and series1[-1] > series2[-1]
    except IndexError:
        return False
