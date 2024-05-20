# TA Library

## TA-Lib

[Home](https://ta-lib.org/functions/) |
[Indicators](https://ta-lib.github.io/ta-lib-python/funcs.html)

### Build from source

Download ta-lib from github [ta-lib-0.4.0-src.tar.gz](https://github.com/TA-Lib/ta-lib/releases/download/v0.4.0/ta-lib-0.4.0-src.tar.gz)

```bash
tar zxvf ta-lib-0.4.0-src.tar.gz
cd ta-lib
./configure --prefix=/usr
make
sudo make install
```

Full install tutorial from [TA-Lib](https://ta-lib.github.io/ta-lib-python/install.html)

### Conda-Forge

```bash
conda install -c conda-forge ta-lib
```

### Python library

```bash
pip install TA-Lib
```

## Pandas-TA

[Home](https://twopirllc.github.io/pandas-ta/) |
[Indicators](https://twopirllc.github.io/pandas-ta/#indicators-by-category)

```bash
pip install pandas_ta
```

## Tulip Indicators

[Home](https://tulipindicators.org/) |
[Indicators](https://tulipindicators.org/list)

### Python library

```bash
pip install Cython numpy
pip install tulipy
```

### Build C library from source [option]

```bash
git clone https://github.com/TulipCharts/tulipindicators
cd tulipindicators
make
```

!!! example
    === "Unordered List"

        ``` markdown
        * Sed sagittis eleifend rutrum
        * Donec vitae suscipit est
        * Nulla tempor lobortis orci
        ```

    === "Ordered List"

        ``` markdown
        1. Sed sagittis eleifend rutrum
        2. Donec vitae suscipit est
        3. Nulla tempor lobortis orci
        ```
