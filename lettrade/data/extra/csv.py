import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)


def csv_export(
    df: pd.DataFrame,
    path: str | Path = "data/data.csv",
    tz=None,
    **kwargs,
):
    df = df.astype(
        dtype={
            "open": "float",
            "high": "float",
            "low": "float",
            "close": "float",
            "volume": "float",
        }
    )

    if not isinstance(df.index, pd.DatetimeIndex):
        df = df.set_index("datetime")

    if tz is not None:
        df.index = df.index.tz_convert(tz)

    if not isinstance(path, Path):
        path = Path(path)

    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, **kwargs)

    logger.info("Saved data to %s", path)
    return df
