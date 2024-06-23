# CCXT exchange

## Installation

```bash
pip install lettrade[exchange-ccxt]
```

## Default config

```python
from lettrade.exchange.live.ccxt import let_ccxt

lt = let_ccxt(
    strategy=SmaCross,
    datas=[("BTC/USD", "1m", "BTCUSD_1m")],
    ccxt_exchange=os.getenv("CCXT_EXCHANGE"),
    ccxt_type=os.getenv("CCXT_TYPE"),
    ccxt_key=os.getenv("CCXT_KEY"),
    ccxt_secret=os.getenv("CCXT_SECRET"),
    ccxt_verbose=os.getenv("CCXT_VERBOSE", "").lower() in ["true", "1"],
)
```

## Example

```python
--8<-- "example/ccxt/ccxt_ema.py"
```
