import logging
import re
from typing import Optional

import pandas as pd

from .timeframe import TimeFrame

logger = logging.getLogger(__name__)


# Base class for DataFeed
_data_name_pattern = re.compile(r"^[\w\_]+$")


class BaseDataFeed(pd.DataFrame):
    """Data for Strategy. A implement of pandas.DataFrame"""

    _lt_pointers: list[int] = [0]

    def __init__(
        self,
        *args,
        name: str,
        # data: pd.DataFrame,
        timeframe: TimeFrame,
        meta: Optional[dict] = None,
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
                f"Bot name {name} is not valid format {_data_name_pattern}"
            )

        # Init
        super().__init__(*args, **kwargs)

        # Metadata
        if not meta:
            meta = dict()
        meta["name"] = name
        meta["timeframe"] = TimeFrame(timeframe)
        self.attrs = {"lt_meta": meta}

    def copy(self, deep=False, *args, **kwargs) -> "BaseDataFeed":
        df = super().copy(deep=deep, *args, **kwargs)
        df = self.__class__(
            data=df,
            name=self.name,
            timeframe=self.timeframe,
            meta=self.meta.copy(),
        )
        return df

    # Functions
    def _set_main(self):
        """Set this dataframe is main datafeed"""
        self.meta["is_main"] = True

    def bar(self, i=0) -> pd.Timestamp:
        raise NotImplementedError("Method is not implement yet")

    def ibar(self, i=0) -> pd.Timestamp:
        raise NotImplementedError("Method is not implement yet")

    def push(self, rows: list):
        raise NotImplementedError("Method is not implement yet")

    def next(self, next=1):
        raise NotImplementedError("Method is not implement yet")

    @property
    def meta(self) -> dict:
        return self.attrs["lt_meta"]

    @property
    def name(self) -> str:
        return self.meta["name"]

    @property
    def timeframe(self) -> TimeFrame:
        return self.meta["timeframe"]

    @property
    def is_main(self) -> bool:
        return self.meta.get("is_main", False)

    @property
    def now(self) -> pd.Timestamp:
        raise NotImplementedError("Method is not implement yet")
