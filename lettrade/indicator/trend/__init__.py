from .ichimoku import ichimoku
from .ma import ema, ma


def pandas_inject(obj: object | None = None):
    if obj is None:
        from pandas.core.base import PandasObject

        obj = PandasObject

    from ..series import series_indicator_inject

    obj.ma = series_indicator_inject(ma)
    obj.ema = series_indicator_inject(ema)
    obj.ichimoku = ichimoku
