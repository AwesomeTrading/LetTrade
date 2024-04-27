import pandas as pd


class DataFeed(pd.DataFrame):
    def __init__(self, name, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.attrs = {"name": name}

    def __getitem__(self, i):
        if isinstance(i, int):
            print(f"[TEST] DataFeed get item {i}")
            return self.loc[i]
        return super().__getitem__(i)

    @property
    def p(self):
        return self.attrs
