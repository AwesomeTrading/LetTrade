from .candlestick import cdl_direction
from .talib import cdl_3blackcrows, cdl_3whitesoldiers, cdl_pattern


def pandas_inject(obj: object | None = None):
    if obj is None:
        from pandas.core.base import PandasObject

        obj = PandasObject

    obj.cdl_direction = cdl_direction

    obj.cdl_3blackcrows = cdl_3blackcrows
    obj.cdl_3whitesoldiers = cdl_3whitesoldiers
    obj.cdl_pattern = cdl_pattern
