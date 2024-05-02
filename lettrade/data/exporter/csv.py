import logging
from pathlib import Path

import pandas as pd
import pytz

logger = logging.getLogger(__name__)


def csv_export(dataframe: pd.DataFrame, path: str | Path = "data/data.csv", **kwargs):
    dataframe = dataframe.astype(
        dtype={
            "open": "float",
            "high": "float",
            "low": "float",
            "close": "float",
            "volume": "float",
        }
    )
    dataframe.index = dataframe.index.tz_convert(pytz.utc)

    if not isinstance(path, Path):
        path = Path(path)

    path.parent.mkdir(parents=True, exist_ok=True)
    dataframe.to_csv(path, **kwargs)

    logger.info("Saved data to %s", path)
    return dataframe
