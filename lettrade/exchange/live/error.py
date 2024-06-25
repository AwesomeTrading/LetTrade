from lettrade.base.error import LetException
from lettrade.exchange import LetOrderInvalidException


class LetLiveException(LetException):
    raw: dict

    def __init__(self, *args: object, raw: dict = None) -> None:
        super().__init__(*args)
        self.raw = raw


class LetLiveAPIUnauthorizedException(LetLiveException):
    """API Unauthorized exception"""


class LetLiveOrderInvalidException(LetLiveException, LetOrderInvalidException):
    """Live order place is invalid exception"""
