import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="lettrade",
    version="0.0.1",
    author="Santatic",
    # author_email = "author@example.com",
    description="Lightweight trading framwork",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AwesomeTrading/lettrade",
    classifiers=[
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Science/Research",
        "Framework :: Jupyter",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Scientific/Engineering :: Visualization",
    ],
    package_dir={"": "lettrade"},
    packages=setuptools.find_packages(where="lettrade"),
    python_requires=">=3.8.0,<3.11",
    install_requires=["pandas", "numpy"],
    extras_require={
        "extra": ["pandas_ta", "plotly"],
        "exchange-metatrader": [
            "mt5linux @ git+https://github.com/AwesomeTrading/mt5linux.git@master"
        ],
        "commander": ["python-telegram-bot"],
        "backtest-extra": ["yfinance"],
        "dev": ["yfinance", "pytz"],
    },
)
