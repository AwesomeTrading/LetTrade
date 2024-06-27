from .keltner_channel import keltner_channel


def pandas_inject(obj: object | None = None):
    if obj is None:
        from pandas.core.base import PandasObject

        obj = PandasObject

    obj.keltner_channel = keltner_channel
