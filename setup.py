if __name__ == "__main__":
    from setuptools import find_packages, setup

    with open("README.md", encoding="utf-8") as fh:
        long_description = fh.read()

    setup(
        name="lettrade",
        version="0.0.10-beta-0",
        author="Santatic",
        # author_email = "author@example.com",
        description="Lightweight trading framwork",
        long_description=long_description,
        long_description_content_type="text/markdown",
        url="https://github.com/AwesomeTrading/LetTrade",
        classifiers=[
            "Intended Audience :: Financial and Insurance Industry",
            "Intended Audience :: Science/Research",
            "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
            "Operating System :: OS Independent",
            "Programming Language :: Python :: 3 :: Only",
            "Programming Language :: Python :: 3.10",
            "Programming Language :: Python :: 3.11",
            "Programming Language :: Python :: 3.12",
            "Topic :: Office/Business :: Financial :: Investment",
            "Topic :: Scientific/Engineering :: Visualization",
        ],
        packages=find_packages(),
        python_requires=">=3.10,<3.13",
        install_requires=["pandas", "numpy<2.0", "numexpr"],
        extras_require={
            "plot": ["plotly"],
            "jupyter": ["nbformat", "rich[jupyter]"],
            "commander": ["lettrade[plot]"],
            "commander-telegram": ["lettrade[commander]", "python-telegram-bot"],
            "backtest": ["lettrade[plot]", "rich"],
            "backtest-extra": ["lettrade[backtest]", "lettrade[jupyter]", "yfinance"],
            "live": ["lettrade[plot]"],
            "exchange-metatrader": [
                "lettrade[live]",
                "python-box",
                "mt5linux",
                # "mt5linux @ git+https://github.com/AwesomeTrading/mt5linux.git@master"
            ],
            "exchange-ccxt": ["lettrade[live]", "ccxt", "python-box"],
            "test": ["pytest"],
            "all": [
                "lettrade[backtest-extra]",
                "lettrade[exchange-metatrader]",
                "lettrade[exchange-ccxt]",
                "lettrade[commander-telegram]",
                "lettrade[test]",
            ],
        },
    )
