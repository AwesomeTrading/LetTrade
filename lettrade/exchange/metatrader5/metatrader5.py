from mt5linux import MetaTrader5 as Mt5


class MetaTrader5:
    _mt5: Mt5

    def __new__(self: "MetaTrader5", *args, **kwargs):
        if not hasattr(self, "_singleton"):
            self._singleton = object.__new__(self)
            self._singleton.init(*args, **kwargs)
        return self._singleton

    def init(self, host="localhost", port=18812) -> None:
        self._mt5 = Mt5(
            host=host,
            port=port,
        )

        self._mt5.initialize()

    def start(self):
        self._mt5.terminal_info()
        self._mt5.copy_rates_from_pos("GOOG", self._mt5.TIMEFRAME_M1, 0, 1000)

    def stop(self):
        self._mt5.shutdown()


mt5 = MetaTrader5()
mt5.start()
mt5.stop()
