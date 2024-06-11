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

    def next(self):
        """"""

    def stop(self):
        """"""

    # Public
    @abstractmethod
    def heartbeat(self):
        """"""

    # Market
    @abstractmethod
    def market(self, symbol: str):
        """"""

    @abstractmethod
    def markets(self, symbols: list[str]):
        """"""

    # Bars
    @abstractmethod
    def bars(self, **kwargs):
        """"""

    # Tick
    @abstractmethod
    def tick_get(self, symbol):
        """"""

    ### Private
    # Account
    @abstractmethod
    def account(self):
        """"""

    #  Order
    @abstractmethod
    def order_open(self, **kwargs):
        """"""

    @abstractmethod
    def order_update(self, order: "LiveOrder", sl=None, tp=None, **kwargs):
        """"""

    @abstractmethod
    def order_close(self, order: "LiveOrder", **kwargs):
        """"""

    @abstractmethod
    def orders_total(self):
        """"""

    @abstractmethod
    def orders_get(self, **kwargs):
        """"""

    # Trade
    @abstractmethod
    def trades_total(self):
        """"""

    @abstractmethod
    def trades_get(self, **kwargs):
        """"""

    @abstractmethod
    def trade_update(self, trade: "LiveTrade", sl=None, tp=None, **kwargs):
        """"""
