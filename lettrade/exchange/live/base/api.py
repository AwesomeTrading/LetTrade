import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class LiveAPI(ABC):
    @classmethod
    def multiprocess(cls, kwargs: dict, **other_kwargs):
        """"""

    def __init__(self, **kwargs):
        """"""

    def init(self, **kwargs):
        """"""

    def start(self, callbacker=None):
        """"""

    def stop(self):
        """"""

    def next(self):
        """"""

    @abstractmethod
    def heartbeat(self):
        """"""

    @abstractmethod
    def account(self):
        """"""

    @abstractmethod
    def markets(self, symbol):
        """"""

    @abstractmethod
    def tick_get(self, symbol):
        """"""

    @abstractmethod
    def order_send(self, **kwargs):
        """"""

    @abstractmethod
    def orders_total(self):
        """"""

    @abstractmethod
    def orders_get(self, **kwargs):
        """"""

    @abstractmethod
    def positions_total(self):
        """"""

    @abstractmethod
    def positions_get(self, **kwargs):
        """"""

    @abstractmethod
    def bars(self, **kwargs):
        """"""
