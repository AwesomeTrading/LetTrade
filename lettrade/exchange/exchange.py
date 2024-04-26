from typing import Optional

from lettrade.data import DataFeed


class Exchange:
    datas: list[DataFeed] = None

    def __init__(self, datas: list[DataFeed] = None) -> None:

        if datas:
            self._load(datas=datas)

    def _load(self, datas: list[DataFeed] = None):
        if datas is not None:
            if self.datas:
                print("[WARN] Reloading datas...")

            self.datas = datas
            self.data = datas[0]

    def new_order(
        self,
        *,
        size: float,
        limit: Optional[float] = None,
        stop: Optional[float] = None,
        sl: Optional[float] = None,
        tp: Optional[float] = None,
        tag: object = None,
    ):
        pass
