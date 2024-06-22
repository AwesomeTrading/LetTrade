from .candlestick import *
from .function import *
from .indicator import *
from .trend import *
from .volatility import *


def indicators_inject_pandas():
    """Inject indicators to Pandas"""
    from pandas.core.base import PandasObject

    if hasattr(PandasObject, "_lt_indicators_injected"):
        return

    from .candlestick import pandas_inject as candlestick_pandas_inject
    from .function import pandas_inject as function_pandas_inject
    from .trend import pandas_inject as trend_pandas_inject
    from .volatility import pandas_inject as volatility_pandas_inject

    function_pandas_inject()

    candlestick_pandas_inject()
    trend_pandas_inject()
    volatility_pandas_inject()

    PandasObject._lt_indicators_injected = True
