import numpy as np
import pandas as pd


class DataFeed(pd.DataFrame):

    def __init__(
        self,
        name,
        info={},
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

        super().__init__(*args, **kwargs)

        info["name"] = name
        self.attrs = {"info": info}

    def __getitem__(self, i):
        if isinstance(i, int):
            print(f"[TEST] DataFeed get item {i}")
            return self.loc[i]
        return super().__getitem__(i)

    @property
    def info(self):
        return self.attrs["info"]
