from .ema import ema
from .ichimoku import ichimoku


def pandas_inject():
    from pandas.core.base import PandasObject

    PandasObject.ema = ema
    PandasObject.ichimoku = ichimoku
