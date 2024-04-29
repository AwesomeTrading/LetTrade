import logging

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


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
            logger.warning("[TEST] DataFeed get item %s", i)
            return self.loc[i]
        return super().__getitem__(i)

    @property
    def meta(self):
        return self.attrs["meta"]
