import numpy as np
import pandas as pd

from . import fastfinance as ff


def ema(
    data: pd.Series | pd.DataFrame,
    period: int,
    smoothing: float = 2.0,
) -> pd.Series | np.ndarray:
    if isinstance(data, pd.DataFrame):
        data = data.close
    return pd.Series(
        ff.ema(data.to_numpy(), period=period, smoothing=smoothing),
        index=data.index,
    )
