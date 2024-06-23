from lettrade.base.error import LetException


class LetNoMoreDataFeedException(LetException):
    """DataFeeder has no more data to feed"""
