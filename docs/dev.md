# Contributing

Contributions are welcome, and they are greatly appreciated! Every little bit helps, and credit will always be given.

# Development

Guide for developer to install `lettrade`

## Environment setup

Set up conda environment

```sh
conda create -y -n LetTrade python=3.10
conda activate LetTrade
conda install -c conda-forge ta-lib
pip install -r requirements-dev.txt
```

## Document

Building `lettrade` document guide

### Dependencies

Install `lettrade` as module

```bash
pip install .
```

Install python document requirements

```bash
pip install -r docs/requirements-docs.txt
```

### View document

Start mkdocs local server

```bash
mkdocs serve
```
