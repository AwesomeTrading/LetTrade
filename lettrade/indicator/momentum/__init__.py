from .rsi import rsi
from .stochastic import stochastic


def pandas_inject(obj: object | None = None):
    if obj is None:
        from pandas.core.base import PandasObject

        obj = PandasObject

    from ..series import series_indicator_inject

    obj.rsi = series_indicator_inject(rsi)
    obj.stochastic = series_indicator_inject(stochastic)
