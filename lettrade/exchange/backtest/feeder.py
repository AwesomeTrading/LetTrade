import logging

from lettrade.data import DataFeeder, LetNoMoreDataFeedException

from .data import BackTestDataFeed

logger = logging.getLogger(__name__)


class BackTestDataFeeder(DataFeeder):
    """BackTest DataFeeder"""

    datas: list[BackTestDataFeed]
    data: BackTestDataFeed

    _start_size: int

    def __init__(self, start_size: int = 500) -> None:
        super().__init__()
        self._start_size = start_size

    @property
    def is_continous(self):
        """Flag check is realtime continous datafeeder"""
        return False

    def start(self, size: int = 0):
        # self._cleanup_data()
        if not size:
            size = self._start_size

        next = self.data.l.index[size]
        for data in self.datas:
            data.next(
                size=size,
                next=next,
                missing="bypass",
            )

    # def _cleanup_data(self):
    #     # Synchronize start time
    #     start = self.data.now
    #     tf = self.data.timeframe
    #     for data in self.datas:
    #         if data is self.data:
    #             continue

    #         if data.timeframe <= tf:
    #             data_start = start
    #         else:
    #             data_start = start - data.timeframe

    #         df = data[data["datetime"] < data_start]
    #         logger.info(
    #             "BackTestDataFeed %s dropped %d rows from start",
    #             data.name,
    #             len(df.index),
    #         )
    #         data.drop(index=df.index, inplace=True)
    #         data.reset_index(inplace=True)

    def next(self):
        next = self.data.l.index[1]

        no_next = 0
        for data in self.datas:
            if not data.next(next=next):
                if data is self.data:
                    raise LetNoMoreDataFeedException()
                no_next += 1

        if no_next >= len(self.datas):
            # Skip lastest available bar, because if next some data feeded some are not
            raise LetNoMoreDataFeedException()

    def alive(self):
        return self.data.alive()
