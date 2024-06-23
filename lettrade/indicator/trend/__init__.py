from ..series import series_indicator_inject
from .ema import ema
from .ichimoku import ichimoku


def pandas_inject():
    from pandas.core.base import PandasObject

    PandasObject.ema = series_indicator_inject(ema)
    PandasObject.ichimoku = ichimoku
