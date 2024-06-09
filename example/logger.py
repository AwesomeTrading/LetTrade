import importlib.util
import logging

coloredlogs = importlib.util.find_spec("coloredlogs")
if coloredlogs:
    import coloredlogs

    coloredlogs.DEFAULT_FIELD_STYLES["funcName"] = dict(color="cyan")

    coloredlogs.install(
        level="INFO",
        fmt="%(asctime)s,%(msecs)03d %(levelname)6s %(name)16s %(funcName)16s(): %(message)s",
    )

logging.basicConfig(level=logging.INFO)


def logging_filter_necessary_only():
    logging.getLogger("lettrade.exchange.backtest.commander").setLevel(logging.WARNING)
    logging.getLogger("lettrade.exchange.backtest.exchange").setLevel(logging.WARNING)
    logging.getLogger("lettrade.exchange.backtest.data").setLevel(logging.WARNING)
    logging.getLogger("lettrade.exchange.order").setLevel(logging.WARNING)
    logging.getLogger("lettrade.bot").setLevel(logging.WARNING)
