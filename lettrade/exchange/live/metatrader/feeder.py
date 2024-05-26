import time

from lettrade.exchange.live.base import LiveDataFeeder

from .api import MetaTraderAPI
from .data import MetaTraderDataFeed


class MetaTraderDataFeeder(LiveDataFeeder):
    """"""
