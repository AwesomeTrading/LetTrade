import logging
from typing import Optional

from lettrade.data import DataFeed
from lettrade.exchange import OrderResult, OrderType
from lettrade.exchange.live.base import LiveExchange

from .api import MetaTraderAPI
from .trade import MetaTraderExecute, MetaTraderOrder, MetaTraderTrade

logger = logging.getLogger(__name__)


class MetaTraderExchange(LiveExchange):
    """MetaTrade 5 exchange module for `lettrade`"""
