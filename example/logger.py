import importlib.util
import logging

rich = importlib.util.find_spec("rich")
if rich:
    from rich.logging import RichHandler

    FORMAT = "%(message)s"
    logging.basicConfig(
        level=logging.root.level,
        format="%(funcName)16s(): %(message)s",
        datefmt="[%X]",
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
