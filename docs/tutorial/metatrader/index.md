# MetaTrader exchange

## Installation

```bash
pip install lettrade[exchange-metatrader]
```

## Default config

```python
from lettrade.exchange.metatrader import let_metatrader


lt = let_metatrader(
    strategy=SmaCross,
    datas=[("EURUSD", "1m")],
    mt5_login=int(os.environ["MT5_LOGIN"]),
    mt5_password=os.environ["MT5_PASSWORD"],
    mt5_server=os.environ["MT5_SERVER"],
    mt5_wine=os.getenv("MT5_WINE", None),
)
```

## Example

```python
--8<-- "example/metatrader/mt5_ema.py"
```
