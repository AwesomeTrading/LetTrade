from ..series import series_indicator_inject
from .ema import ema
from .ichimoku import ichimoku


def pandas_inject(obj: object | None = None):
    if obj is None:
        from pandas.core.base import PandasObject

        obj = PandasObject

    obj.ema = series_indicator_inject(ema)
    obj.ichimoku = ichimoku
