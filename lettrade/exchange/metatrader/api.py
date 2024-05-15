import logging
from time import sleep

from mt5linux import MetaTrader5 as Mt5

logger = logging.getLogger(__name__)


TIMEFRAME_L2M = {
    "1m": Mt5.TIMEFRAME_M1,
    "2m": Mt5.TIMEFRAME_M2,
    "3m": Mt5.TIMEFRAME_M3,
    "4m": Mt5.TIMEFRAME_M4,
    "5m": Mt5.TIMEFRAME_M5,
    "6m": Mt5.TIMEFRAME_M6,
    "10m": Mt5.TIMEFRAME_M10,
    "12m": Mt5.TIMEFRAME_M12,
    "15m": Mt5.TIMEFRAME_M15,
    "20m": Mt5.TIMEFRAME_M20,
    "30m": Mt5.TIMEFRAME_M30,
    "1h": Mt5.TIMEFRAME_H1,
    "2h": Mt5.TIMEFRAME_H2,
    "3h": Mt5.TIMEFRAME_H3,
    "4h": Mt5.TIMEFRAME_H4,
    "6h": Mt5.TIMEFRAME_H6,
    "8h": Mt5.TIMEFRAME_H8,
    "12h": Mt5.TIMEFRAME_H12,
    "1d": Mt5.TIMEFRAME_D1,
    "1w": Mt5.TIMEFRAME_W1,
    "1mn": Mt5.TIMEFRAME_MN1,
}


class MetaTraderAPI:
    _mt5: Mt5

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_singleton"):
            cls._singleton = object.__new__(cls)
            cls._singleton.__init__(*args, **kwargs)
        return cls._singleton

    def __init__(self, host="localhost", port=18812) -> None:
        self._mt5 = Mt5(host=host, port=port)

    def start(self, account: int, password: str, server: str, timeout=60, retry=20):
        while retry > 0:
            login = self._mt5.initialize(
                login=int(account),
                password=password,
                server=server,
                # timeout=timeout,
            )
            if login:
                break

            if __debug__:
                logger.info("Login retry: %d", retry)

            sleep(1)
            retry -= 1

        if retry == 0:
            raise RuntimeError(f"Cannot login {account}")

        logger.info(
            "Login success account=%s, server=%s, version=%s",
            account,
            server,
            self._mt5.version(),
        )

        terminal = self._mt5.terminal_info()
        logger.info("Terminal information: %s", str(terminal))
        if not terminal.trade_allowed:
            logger.warning("Terminal trading mode is not allowed")

    def stop(self):
        self._mt5.shutdown()

    def heartbeat(self):
        return True

    def account(self):
        return self._mt5.account_info()

    def markets(self, symbol):
        return self._mt5.symbol_info(symbol)

    def tick(self, symbol):
        return self._mt5.symbol_info_tick(symbol)

    def rates_from_pos(self, symbol, timeframe, since=0, to=1000):
        rates = self._mt5.copy_rates_from_pos(
            symbol,
            TIMEFRAME_L2M[timeframe],
            since,
            to,
        )
        return rates

    def order_send(self, request: "TradeRequest"):
        return self._mt5.order_send(request)
