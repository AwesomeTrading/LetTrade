import logging

from lettrade.commander import Commander

logger = logging.getLogger(__name__)


class BackTestCommander(Commander):
    """
    BackTest Commander to debug commander notify
    """

    def start(self):
        logger.debug("BackTestCommander start")

    def stop(self):
        logger.debug("BackTestCommander stop")

    def send_message(self, msg: str, **kwargs):
        logger.info("BackTestCommander send_message: %s, %s", msg, kwargs)
