from .atr import atr
from .bollinger_bands import bollinger_bands
from .keltner_channel import keltner_channel


def pandas_inject(obj: object | None = None):
    if obj is None:
        from pandas.core.base import PandasObject

        obj = PandasObject

    from ..series import series_indicator_inject

    obj.bollinger_bands = series_indicator_inject(bollinger_bands)

    obj.keltner_channel = keltner_channel
    obj.atr = atr
