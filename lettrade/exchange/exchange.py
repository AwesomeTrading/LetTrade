from typing import Optional

from lettrade.data import DataFeed


class Exchange:
    datas: list[DataFeed] = None

    def __init__(self) -> None:
        pass

    def _load(self, feeder):
        if self.datas:
            print("[WARN] Reloading datas...")
        print(feeder.datas)
        self.datas = feeder.datas
        self.data = feeder.datas[0]

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
