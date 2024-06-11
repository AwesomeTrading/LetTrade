if __name__ == "__main__":
    from setuptools import find_packages, setup

    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()

    setup(
        name="lettrade",
        version="0.0.3",
        author="Santatic",
        # author_email = "author@example.com",
        description="Lightweight trading framwork",
        long_description=long_description,
        long_description_content_type="text/markdown",
        url="https://github.com/AwesomeTrading/lettrade",
        classifiers=[
            "Intended Audience :: Financial and Insurance Industry",
            "Intended Audience :: Science/Research",
            "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
            "Operating System :: OS Independent",
            "Programming Language :: Python :: 3 :: Only",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python :: 3.10",
            "Programming Language :: Python :: 3.11",
            "Programming Language :: Python :: 3.12",
            "Topic :: Office/Business :: Financial :: Investment",
            "Topic :: Scientific/Engineering :: Visualization",
        ],
        packages=find_packages(),
        python_requires=">=3.8.0,<3.13",
        install_requires=["pandas", "numpy"],
        extras_require={
            "extra": ["pandas_ta", "plotly", "nbformat"],
            "backtest": ["tqdm", "plotly"],
            "backtest-extra": ["yfinance"],
            "commander": ["python-telegram-bot"],
            "dev": ["yfinance", "pytz"],
            "exchange-metatrader": [
                # "mt5linux @ git+https://github.com/AwesomeTrading//mt5linux.git@master"
            ],
            "exchange-ccxt": ["ccxt"],
        },
    )
