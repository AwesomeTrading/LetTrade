from unittest.mock import MagicMock

import pytest
from box import Box
from pytest_mock import MockerFixture

from lettrade.exchange.live.metatrader.api import MT5, MetaTraderAPI

_api_module_path = "lettrade.exchange.live.metatrader.api"
_api_class_path = f"{_api_module_path}.MetaTraderAPI"


@pytest.fixture
def metatrader_api(mocker: MockerFixture):
    mocker.patch(f"{_api_module_path}.MT5.account_info", return_value=Box(login=123))
    mocker.patch(f"{_api_module_path}.MT5.initialize", return_value=True)
    mocker.patch(
        f"{_api_module_path}.MT5.terminal_info",
        return_value=Box({"trade_allowed": True}),
    )
    mocker.patch(f"{_api_module_path}.MT5.history_deals_get", return_value=True)
    mocker.patch(f"{_api_module_path}.MT5.orders_get", return_value=True)
    mocker.patch(f"{_api_module_path}.MT5.positions_get", return_value=True)
    mocker.patch("time.sleep", return_value=MagicMock())

    return MetaTraderAPI(
        login=123,
        password="password",
        server="pytest",
    )


def test_init_api(metatrader_api):
    MT5.account_info.assert_called_once()
