from .keltner_channel import keltner_channel


def pandas_inject():
    from pandas.core.base import PandasObject

    PandasObject.keltner_channel = keltner_channel
