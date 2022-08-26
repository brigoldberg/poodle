import os
import sys
import pandas as pd


class Quoter:

    TICK_DS = os.path.expanduser('~/tick_data/ohlc.h5')
    
    @classmethod
    def get_price(obj, ticker, trade_date, column_select=None):

        hdf = pd.HDFStore(obj.TICK_DS, mode='r')
        try:
            stock_price = hdf[ticker].loc[trade_date]
        except KeyError:
            return None        
        hdf.close()

        if column_select:
            return stock_price[column_select]

        return stock_price
