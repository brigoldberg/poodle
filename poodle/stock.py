# stock.py
import os
import sys
import pandas as pd
import toml
from .utils import read_config
from .applogger import get_logger


class Stock:
    """
    Create object for storing both historical OHLC data but also
    trading/sim data such as trade logs, PnL and shares held.
    
    Can be instantiated on its own but is typically called from a
    Universe object and the configuration is passed into the Stock
    object.
    """

    def __init__(self, symbol, **kwargs):
        """
        Create object -> Load data -> Snip dates
        """
        self.symbol = symbol.lower()
        self.tsdb   = None
        self.signal = None
        self.trade_log = None

        # Every stock object should read/get configuration
        _config =  kwargs.get('config', {})
        if type(_config) is not dict:
            self.config = read_config(_config)
        else:
            self.config = _config

        log_level   = self.config['logging']['log_level']
        self.logger = get_logger(f'stock-{self.symbol}', log_level)

        self.tick_ds  = self.config['data_source']['hdf5_file']
        self.col_name = self.config['data_map']['column_name']

        self._load_data()

        # The trade_log holds all transactions and position & PnL is calculated
        # from this data structure.
        self.trade_log = pd.DataFrame(index=self.tsdb.index, dtype='float64')
        self.trade_log['shares']        = 0
        self.trade_log['trade_price']   = 0

    def _load_data(self):
        """ Load data from HDF5 source and create associated time series. """
        self.tsdb = pd.read_hdf(self.tick_ds, key=f'/{self.symbol}')
        self.tsdb['pct_ret'] = self.tsdb[self.col_name].pct_change()
        # create empty signal Series
        self.signal = pd.Series(index=self.tsdb.index, dtype='float64')
        self.logger.info(f'{self.symbol.upper()}: loaded tsdb and set empty signal')

    def snip_dates(self, date_start, date_end):
        """ Prune rows from beginning and/or ends of the TSDB. """
        self.tsdb      = self.tsdb.loc[date_start:date_end]
        self.signal    = self.signal.loc[date_start:date_end]
        self.trade_log = self.trade_log.loc[date_start:date_end]
        self.logger.info(f'{self.symbol.upper()}: pruned dates {date_start} to {date_end}')            
    def log_trade(self, trade_date, shares, price):
        if trade_date not in self.trade_log.index:
            raise Exception(f'{trade_date} not in time series')
        self.trade_log.loc[trade_date, ['shares', 'trade_price']] = [shares, price]

    def get_book_value(self, trade_date):
        """ Return dollar value of all shares at specified trade_date """
        shares = self.trade_log['shares'].loc[:trade_date].sum()
        spot_price = self.tsdb[self.col_name].loc[trade_date]
        book_value = shares * spot_price
        self.logger.info(f'{self.symbol.upper()}: book value {shares}@${spot_price} is ${book_value:0.2f}')
        return book_value

    def get_book_cost(self, trade_date):
        """ Return cost of all stock purchases up to submitted date """
        total_book_cost = self.trade_log['shares'] * self.trade_log['trade_price']    
        book_cost =total_book_cost.loc[:trade_date].sum()
        self.logger.info(f'{self.symbol.upper()}: book cost ${book_cost:0.2f}')
        return book_cost

    def get_book_pnl(self, trade_date):
        """ Return PnL of all trades up to submitted trade date """
        book_pnl = self.get_book_value(trade_date) - self.get_book_cost(trade_date)
        self.logger.info(f'{self.symbol.upper()}: book PnL ${book_pnl:0.2f}')
        return book_pnl
