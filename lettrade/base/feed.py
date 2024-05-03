from typing import Any


class BaseDataFeeds:
    """
    Base class help to quick get direct feeder datas
    """

    feeder: "DataFeeder"

    @property
    def data(self) -> "DataFeed":
        return self.feeder.data

    @property
    def datas(self) -> list["DataFeed"]:
        return self.feeder.datas
