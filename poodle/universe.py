# universe.py
import os
import sys
import toml
from .stock import Stock
from .utils import iterate_basket, read_config
from .applogger import get_logger


class Universe:
    """
    Create a 'baslket'  of Stock object from list of symbols.
    """
    def __init__(self, symbol_list, *args, **kwargs):

        self.stocks = {}

        _config =  kwargs.get('config', {})
        if type(_config) is not dict:
            self.config = read_config(_config)
        else:
            self.config = _config

        log_level   = self.config['logging']['log_level']
        self.logger = get_logger(f'universe', log_level)

        for symbol in symbol_list:
            self.stocks[symbol] = Stock(symbol, config=self.config)
            self.logger.info(f'adding {symbol} to universe')

    @iterate_basket
    def list_basket(self, stock_obj):
        print(f'{stock_obj.symbol}')

    @iterate_basket
    def set_date_range(self, stock_obj, date_start, date_end):
        stock_obj.snip_dates(date_start, date_end)
