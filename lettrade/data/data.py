import logging
import re
from datetime import datetime
from typing import Optional

import pandas as pd

logger = logging.getLogger(__name__)
_data_name_pattern = re.compile(r"^[\w\_]+$")


class DataFeed(pd.DataFrame):
    """Data for Strategy. A implement of pandas.DataFrame"""

    def __init__(
        self,
        name: str,
        # data: pd.DataFrame,
        meta: Optional[dict] = None,
        # dtype={},
        *args,
        **kwargs,
    ) -> None:
        """_summary_

        Args:
            name (str): Name of DataFeed
            meta (Optional[dict], optional): metadata of DataFeed. Defaults to None.
            *args (list): `pandas.DataFrame` list parameters
            **kwargs (dict): `pandas.DataFrame` dict parameters
        """
        # Validate
        if not _data_name_pattern.match(name):
            raise RuntimeError(
                "Bot name %s is not valid format %s",
                name,
                _data_name_pattern,
            )

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
        if not isinstance(self.index, pd.RangeIndex):
            self.reset_index(inplace=True)
            # self.index = pd.RangeIndex(start=0, stop=len(self.index), step=1)

        # Metadata
        if not meta:
            meta = dict()
        meta["name"] = name
        self.attrs = {"lt_meta": meta}

    def __getitem__(self, i):
        if isinstance(i, int):
            logger.warning("[TEST] DataFeed get item %s", i)
            return self.loc[i]
        return super().__getitem__(i)

    def copy(self, deep=False, *args, **kwargs) -> "DataFeed":
        df = super().copy(deep=deep, *args, **kwargs)
        df = self.__class__(name=self.name, data=df)
        # df.reset_index(inplace=True)
        return df

    # Properties
    @property
    def meta(self) -> dict:
        return self.attrs["lt_meta"]

    @property
    def name(self) -> str:
        return self.meta["name"]

    @property
    def is_main(self) -> bool:
        return self.meta.get("is_main", False)

    @property
    def now(self) -> datetime:
        return self.datetime[0]

    # Functions
    def bar(self, i=0):
        return self.index[0] + i, self.datetime[i]

    def next(self, size=1) -> bool:
        raise NotImplementedError("Method is not implement yet")

    def _set_main(self):
        """Set this dataframe is main datafeed"""
        self.meta["is_main"] = True
