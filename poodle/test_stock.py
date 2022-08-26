import pytest

from .stock import Stock


def test_create_stock_obj():
    so = Stock('aapl', config='../config.toml')
    #assert type(so) == "poodle.stock.Stock"
    assert so.tsdb['volume'].iloc[0] > 100
