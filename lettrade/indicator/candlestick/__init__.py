from .candlestick import cdl_direction
from .talib import cdl_3blackcrows, cdl_3whitesoldiers, cdl_pattern


def pandas_inject():
    from pandas.core.base import PandasObject

    PandasObject.cdl_direction = cdl_direction

    PandasObject.cdl_3blackcrows = cdl_3blackcrows
    PandasObject.cdl_3whitesoldiers = cdl_3whitesoldiers
    PandasObject.cdl_pattern = cdl_pattern
