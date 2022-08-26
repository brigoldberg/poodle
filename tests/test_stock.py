#!/usr/bin/env python3
# test_stock.py

import sys
import os
import numpy as np
app_path = os.path.join(os.path.expanduser('~/sandbox/poodle/'))
sys.path.append(app_path)
from poodle import Stock


SYMBOL = 'spy'
stock = Stock(SYMBOL, config='../config.toml')
trades = {
    '2015-01-02': 250,
    '2015-08-27': -100,
    '2015-10-02': 75 }

def test_load_data():
    """
    Test correct loading of HDF5 data into dataframe.
    """
    stock.snip_dates('2015-01-01', '2015-12-31')
    assert len(stock.tsdb) == 252

def test_log_trade():
    """
    Log 3 trades and confirm data exists and is correct.
    """
    for trade_date, shares in trades.items():
        stock_price = stock.tsdb.loc[trade_date]['close']
        stock.log_trade(trade_date, shares, stock_price)

    assert stock.trade_log.shares.sum() == 225

def test_get_book_cost():
    """
    Calc cost of purchased stock at date in middle of 
    trade log.
    """
    #assert stock.get_book_cost('2015-09-15') == 40600.25
    assert stock.get_book_cost('2015-09-15') == 27527.00

def test_get_book_value():
    """
    Calc total book value at end of year.
    """
    assert stock.get_book_value('2015-12-31') == 41247.00





