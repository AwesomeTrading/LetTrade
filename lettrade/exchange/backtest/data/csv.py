from pathlib import Path

import pandas as pd


def csv_save(dataframe: pd.DataFrame, path: str | Path = "data/data.csv", **kwargs):
    dataframe = dataframe.astype(
        dtype={
            "open": "float",
            "high": "float",
            "low": "float",
            "close": "float",
            "volume": "float",
        }
    )

    if not isinstance(path, Path):
        path = Path(path)

    path.parent.mkdir(parents=True, exist_ok=True)
    dataframe.to_csv(path, **kwargs)

    print(f"[INFO] saved data to {path}")
