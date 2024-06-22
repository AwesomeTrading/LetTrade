from .candlestick import *
from .dataframe import *
from .series import *
from .trend import *
from .volatility import *


def indicators_inject_pandas():
    """Inject indicators to Pandas"""
    from pandas.core.base import PandasObject

    # Flag to mark indicators injected
    if hasattr(PandasObject, "_lt_indicators_injected"):
        return

    from .candlestick import pandas_inject as candlestick_pandas_inject
    from .dataframe import pandas_inject as dataframe_pandas_inject
    from .series import pandas_inject as series_pandas_inject
    from .trend import pandas_inject as trend_pandas_inject
    from .volatility import pandas_inject as volatility_pandas_inject

    series_pandas_inject()
    dataframe_pandas_inject()

    candlestick_pandas_inject()
    trend_pandas_inject()
    volatility_pandas_inject()

    # Flag to mark indicators injected
    PandasObject._lt_indicators_injected = True
