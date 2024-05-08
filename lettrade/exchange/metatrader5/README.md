# Install
## Ubuntu
```sh
wget https://download.mql5.com/cdn/web/metaquotes.software.corp/mt5/mt5ubuntu.sh ; chmod +x mt5ubuntu.sh ; ./mt5ubuntu.sh
```

## Wine
```sh
wget https://www.python.org/ftp/python/3.10.9/python-3.10.9.exe

# same WINEPREFIX with metatrader
WINEPREFIX=~/.mt5 wine python-3.10.9.exe
```

## Python
```sh
WINEPREFIX=~/.mt5 wine python.exe -m pip install git+https://github.com/lucas-campagna/mt5linux.git@master
```

# Run
```sh
WINEPREFIX=~/.mt5 wine start /ProgIDOpen MetaTrader\\ 5\\ Export\\ File "MetaTrader 5"

WINEPREFIX=~/.mt5 wine "C:\\users\\m3\\AppData\\Roaming\\Microsoft\\Windows\\Start\\ Menu\\Programs\\MetaTrader\ 5\\MetaTrader\ 5.lnk"
```

```sh
cd ~/.mt5/dosdevices/c:/users/m3/AppData/Local/Programs/Python/Python310-32/
WINEPREFIX=~/.mt5 wine python.exe
```