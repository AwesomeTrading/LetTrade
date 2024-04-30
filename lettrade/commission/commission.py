from abc import ABCMeta, abstractmethod


class Commission(metaclass=ABCMeta):

    def __init__(
        self,
        *,
        commission=0.0,
        # multiple=1.0,
        # margin=None,
        leverage=1.0,
    ) -> None:
        self.commission: float = commission
        # self._multiple = multiple
        # self._margin = margin
        self.leverage: float = leverage

    def __repr__(self):
        return "<Commission " + str(self) + ">"
