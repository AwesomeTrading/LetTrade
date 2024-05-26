import logging
from typing import Any, Optional, Type

from mt5linux import MetaTrader5 as mt5

from lettrade.exchange import (
    Execute,
    Order,
    OrderResult,
    OrderResultError,
    OrderResultOk,
    OrderState,
    OrderType,
    Trade,
    TradeState,
)
from lettrade.exchange.live.base import LiveExecute, LiveOrder, LiveTrade

logger = logging.getLogger(__name__)


class MetaTraderExecute(LiveExecute):
    """
    Execute for MetaTrader
    """


class MetaTraderOrder(LiveOrder):
    """"""

    def _build_place_request(self):
        tick = self._api.tick_get(self.data.symbol)
        price = tick.ask if self.is_long else tick.bid
        type = mt5.ORDER_TYPE_BUY if self.is_long else mt5.ORDER_TYPE_SELL
        deviation = 20
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.data.symbol,
            "volume": self.size,
            "type": type,
            "price": price,
            "sl": self.sl,
            "tp": self.tp,
            "deviation": deviation,
            "magic": 234000,
            "comment": self.tag,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        return request


class MetaTraderTrade(LiveTrade):
    """"""
