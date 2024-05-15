# Install
## Wine
Ubuntu
```sh
wget https://download.mql5.com/cdn/web/metaquotes.software.corp/mt5/mt5ubuntu.sh ; chmod +x mt5ubuntu.sh ; ./mt5ubuntu.sh
```

## Python
```sh
wget https://www.python.org/ftp/python/3.10.9/python-3.10.9.exe

# same WINEPREFIX with metatrader
WINEPREFIX=$HOME/.mt5 wine python-3.10.9.exe
```

## Python requirements
```sh
cd $HOME/.mt5/dosdevices/c:/users/$USER/AppData/Local/Programs/Python/Python310-32/
WINEPREFIX=$HOME/.mt5 wine python.exe -m pip install --upgrade pip
WINEPREFIX=$HOME/.mt5 wine python.exe -m pip install MetaTrader5
WINEPREFIX=$HOME/.mt5 wine python.exe -m pip install https://github.com/AwesomeTrading/mt5linux/archive/master.zip
```

# Start Server
```sh
WINEPREFIX=$HOME/.mt5 python -m mt5linux "$HOME/.mt5/dosdevices/c:/users/$USER/AppData/Local/Programs/Python/Python310-32/python.exe"
```

# MetaTrader Terminal
Load broker information before start by steps:
    
`File` -> `Open an Account` -> Search your broker (ex: `Tickmill`, `Roboforex`...) -> `Enter` to load -> `Cancel` (Done)

Enable Automatic Algo Trading

`Tools` -> `Options` -> `Expert Advisors` -> `Allow Auto Trading` -> uncheck `Disable automated trading when switching accounts` and `Disable automated trading when switching profiles`