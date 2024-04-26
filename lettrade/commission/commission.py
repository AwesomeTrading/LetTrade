from abc import ABCMeta, abstractmethod


class Commission(metaclass=ABCMeta):
    _commission: float
    # _multiple: float
    # _margin: float
    _leverage: float

    def __init__(
        self,
        *,
        commission=0.0,
        # multiple=1.0,
        # margin=None,
        leverage=1.0,
    ) -> None:
        self._commission = commission
        # self._multiple = multiple
        # self._margin = margin
        self._leverage = leverage

    def __repr__(self):
        return "<Commission " + str(self) + ">"
