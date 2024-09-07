# MetaTrader exchange

## Installation

### MetaTrader 5

[MetaTrader 5](../../install/metatrader.md)

### Python

```bash
pip install lettrade[exchange-metatrader]
```

## Default config

Example `.env` file

```bash
MT5_LOGIN=123123123
MT5_PASSWORD=qweqweqwe
MT5_SERVER=RoboForex-Demo
MT5_WINE=WINEPREFIX=$HOME/.mt5 python -m mt5linux "$HOME/.mt5/dosdevices/c:/users/$USER/AppData/Local/Programs/Python/Python310-32/python.exe"
```

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
