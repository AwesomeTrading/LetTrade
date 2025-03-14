from .candlestick import *
from .dataframe import *
from .momentum import *
from .plot import DATAFRAME_PLOTTERS_NAME, IndicatorPlotter, indicator_load_plotters
from .series import *
from .trend import *
from .volatility import *


def indicators_inject_pandas(obj: object | None = None):
    """Inject indicators to Pandas"""
    if obj is None:
        from pandas.core.base import PandasObject

        obj = PandasObject

    # Flag to mark indicators injected
    if hasattr(obj, "_lt_indicators_injected"):
        # if __debug__:
        #     print("[WARN] Re-injected indicators")
        return

    from .candlestick import pandas_inject as candlestick_pandas_inject
    from .dataframe import pandas_inject as dataframe_pandas_inject
    from .momentum import pandas_inject as momentum_pandas_inject
    from .series import pandas_inject as series_pandas_inject
    from .trend import pandas_inject as trend_pandas_inject
    from .volatility import pandas_inject as volatility_pandas_inject

    series_pandas_inject(obj)
    dataframe_pandas_inject(obj)

    candlestick_pandas_inject(obj)
    trend_pandas_inject(obj)
    volatility_pandas_inject(obj)
    momentum_pandas_inject(obj)

    # Flag to mark indicators injected
    obj._lt_indicators_injected = True
