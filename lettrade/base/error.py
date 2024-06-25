class LetException(Exception):
    """Base LetTrade exception"""

    @property
    def message(self) -> str:
        return self.args[0] if self.args else ""
