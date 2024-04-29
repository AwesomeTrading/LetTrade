import numpy as np
import pandas as pd


class DataFeed(pd.DataFrame):

    def __init__(
        self,
        name,
        meta={},
        *args,
        **kwargs,
    ) -> None:
        # dtype.update(
        #     {
        #         # "datetime": "datetime64[ns]",
        #         "open": "float",
        #         "high": "float",
        #         "low": "float",
        #         "close": "float",
        #         "volume": "float",
        #     }
        # )
        # print(dtype)
        # df.set_index(pd.DatetimeIndex(df["datetime"]), inplace=True)

        super().__init__(*args, **kwargs)

        meta["name"] = name
        self.attrs = {"lt_meta": meta}

    def __getitem__(self, i):
        if isinstance(i, int):
            print(f"[TEST] DataFeed get item {i}")
            return self.loc[i]
        return super().__getitem__(i)

    @property
    def meta(self):
        return self.attrs["meta"]
