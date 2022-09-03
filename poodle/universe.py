# universe.py
import locale
import os
import sys
import toml
from .stock import Stock
from .utils import iterate_basket, read_config
from .applogger import get_logger
locale.setlocale(locale.LC_ALL, 'en_US')

class Universe:
    """
    Create a 'basket'  of Stock object from list of symbols.
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

    def get_basket_pnl(self, date_end):
        universe_pnl = 0
        for symbol,stock_obj in self.stocks.items():
            symbol_pnl = stock_obj.get_book_pnl(date_end)
            universe_pnl = universe_pnl + symbol_pnl
            self.logger.info(f'{symbol} {symbol_pnl}')

        #print(f"${locale.currency(universe_pnl, grouping=True)}")
        print(f"${locale.format_string('%.2f', universe_pnl, True)}")

    def get_basket_sharpe(self, stock_obj, date_end):
        pass

    def plot_basket_pnl(self, stock_obj, date_end):
        pass
