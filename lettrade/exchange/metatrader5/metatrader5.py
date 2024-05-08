from mt5linux import MetaTrader5 as Mt5


class MetaTrader5:
    _mt5: Mt5

    def __new__(self: "MetaTrader5", *args, **kwargs):
        if not hasattr(self, "_singleton"):
            self._singleton = object.__new__(self)
            self._singleton.init(*args, **kwargs)
        return self._singleton

    def init(self, host="localhost", port=18812) -> None:
        self._mt5 = Mt5(host=host, port=port)

    def start(self, login: int, password: str, server: str, timeout=60):
        login = self._mt5.initialize(
            login=int(login),
            password=password,
            server=server,
            timeout=timeout,
        )

        print("login", login)

        info = self._mt5.terminal_info()
        print("info", info)
        rates = self._mt5.copy_rates_from_pos("EURUSD", self._mt5.TIMEFRAME_M1, 0, 1000)
        print("rates", rates)

    def stop(self):
        self._mt5.shutdown()
