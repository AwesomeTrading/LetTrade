import importlib.util
import logging

rich = importlib.util.find_spec("rich")
if rich:
    from rich.logging import RichHandler

    logging.basicConfig(
        level=logging.INFO,
        format="%(name)-50s %(funcName)32s():\n%(message)s",
        datefmt="[%x %X.%f]",
        handlers=[RichHandler(rich_tracebacks=True)],
    )
else:
    logging.basicConfig(level=logging.INFO)


logging.getLogger("lettrade.data.data").setLevel(logging.DEBUG)
logging.getLogger("lettrade.exchange.live.account").setLevel(logging.DEBUG)


def logging_filter_necessary_only():
    logging.getLogger("lettrade.exchange.backtest.commander").setLevel(logging.WARNING)
    logging.getLogger("lettrade.exchange.backtest.exchange").setLevel(logging.WARNING)
    logging.getLogger("lettrade.exchange.backtest.data").setLevel(logging.WARNING)
    logging.getLogger("lettrade.exchange.order").setLevel(logging.WARNING)
    logging.getLogger("lettrade.bot").setLevel(logging.WARNING)
