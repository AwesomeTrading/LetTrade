from lettrade.base.error import LetException


class LetOrderException(LetException):
    """Base order exception"""


class LetOrderValidateException(LetOrderException):
    """Order attribute validate exception"""


class LetOrderInvalidException(LetOrderException):
    """Order place is invalid exception"""
