# MetaTrader 5 Install

`MetaTrader 5` is exchange server of module [MetaTrader](../reference/exchange/metatrader/metatrader.md)

## Ubuntu

### Wine

```sh
wget https://download.mql5.com/cdn/web/metaquotes.software.corp/mt5/mt5ubuntu.sh ; chmod +x mt5ubuntu.sh ; ./mt5ubuntu.sh
```

### Python

```sh
wget https://www.python.org/ftp/python/3.12.7/python-3.12.7-amd64.exe

export WINEPREFIX=$HOME/.mt5
wine python-3.12.7-amd64.exe
```

### Python requirements

```sh
export WINEPREFIX=$HOME/.mt5

cd $HOME/.mt5/dosdevices/c:/users/$USER/AppData/Local/Programs/Python/Python312/

wine python.exe -m pip install --upgrade pip
wine python.exe -m pip install MetaTrader5
wine python.exe -m pip install 'numpy<1.27'
wine python.exe -m pip install https://github.com/AwesomeTrading/mt5linux/archive/master.zip
```

### Start Server

```sh
export WINEPREFIX=$HOME/.mt5

python -m mt5linux "$HOME/.mt5/dosdevices/c:/users/$USER/AppData/Local/Programs/Python/Python312/python.exe"
```

## MetaTrader Terminal

### Load broker information

Load broker information before start by steps:

- `File` menu
- `Open an Account` action
- Search your broker (ex: `Tickmill`, `Roboforex`...)
- `Enter` to load
- `Cancel` (Done)

### Enable Automatic Algo Trading

- `Tools` menu
- `Options` menu
- `Expert Advisors` tab
- `Allow Auto Trading` checkbox
- Uncheck `Disable automated trading when switching accounts` and `Disable automated trading when switching profiles`
