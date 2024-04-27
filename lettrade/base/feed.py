from typing import Any


class BaseDataFeeds:
    """
    Base class help to quick get direct feeder datas
    """

    feeder: Any

    @property
    def data(self):
        return self.feeder.data

    @property
    def datas(self):
        return self.feeder.datas
