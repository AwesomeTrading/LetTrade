import logging
from datetime import datetime

import pandas as pd

logger = logging.getLogger(__name__)


class DataFeed(pd.DataFrame):

    def __init__(
        self,
        name,
        # data: pd.DataFrame,
        meta={},
        # dtype={},
        *args,
        **kwargs,
    ) -> None:
        # dtype.update(
        #     {
        #         "datetime": "datetime64[ns, UTC]",
        #         "open": "float",
        #         "high": "float",
        #         "low": "float",
        #         "close": "float",
        #         "volume": "float",
        #     }
        # )
        # print(dtype)
        # data.set_index(
        #     pd.DatetimeIndex(data.datetime, dtype="datetime64[ns, UTC]"), inplace=True
        # )
        # print(data.index.tz_convert(pytz.utc))

        super().__init__(*args, **kwargs)
        # if not isinstance(self.index, pd.DatetimeIndex):
        #     self.index = data.index.tz_convert(pytz.utc)
        self.reset_index(inplace=True)

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

    @property
    def now(self) -> datetime:
        return self.datetime[0]

    @property
    def bar(self):
        return self.index
