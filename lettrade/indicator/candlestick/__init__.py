from .candlestick import cdl_direction
from .talib import (
    cdl_3blackcrows,
    cdl_3inside,
    cdl_3whitesoldiers,
    cdl_doji,
    cdl_eveningstar,
    cdl_morningstar,
    cdl_pattern,
)


def pandas_inject(obj: object | None = None):
    if obj is None:
        from pandas.core.base import PandasObject

        obj = PandasObject

    obj.cdl_direction = cdl_direction

    obj.cdl_pattern = cdl_pattern
    obj.cdl_3blackcrows = cdl_3blackcrows
    obj.cdl_3whitesoldiers = cdl_3whitesoldiers
    obj.cdl_morningstar = cdl_morningstar
    obj.cdl_eveningstar = cdl_eveningstar
    obj.cdl_doji = cdl_doji
    obj.cdl_3inside = cdl_3inside
