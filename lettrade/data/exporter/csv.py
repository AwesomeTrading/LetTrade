import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)


def csv_export(
    dataframe: pd.DataFrame,
    path: str | Path = "data/data.csv",
    tz=None,
    **kwargs,
):
    dataframe = dataframe.astype(
        dtype={
            "open": "float",
            "high": "float",
            "low": "float",
            "close": "float",
            "volume": "float",
        }
    )

    if not isinstance(dataframe.index, pd.DatetimeIndex):
        dataframe = dataframe.set_index("datetime")

    if tz is not None:
        dataframe.index = dataframe.index.tz_convert(tz)

    if not isinstance(path, Path):
        path = Path(path)

    path.parent.mkdir(parents=True, exist_ok=True)
    dataframe.to_csv(path, **kwargs)

    logger.info("Saved data to %s", path)
    return dataframe
