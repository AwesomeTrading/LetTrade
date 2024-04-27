import pandas as pd
import pandas_ta as ta


class DataFeed(pd.DataFrame):
    def __init__(self, name, info={}, *args, **kwargs) -> None:
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
