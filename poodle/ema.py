# ema.py
import numpy as np
from .utils import read_config
from .applogger import get_logger


class EMA:
    """
    Calculate trading signal using Exponetial Moving Average patterns.
    """

    def __init__(self, stock_obj, *args, **kwargs):
        
        self.stock_obj = stock_obj
        self.name = 'ema'
        
        self.ema_config = stock_obj.config['strategy']['ema']

        log_level   = self.stock_obj.config['logging']['log_level']
        self.logger = get_logger(f'ema-{self.stock_obj.symbol}', log_level)

        self._calc_basic_ema()
        self._calc_normalized_ema()
        #self._calc_signal_basic_ema()
        self._calc_signal_stupid_ema()

    def _calc_basic_ema(self):

        col_name = self.stock_obj.config['data_map']['column_name']
        window   = self.ema_config['window']

        self.stock_obj.tsdb['ema'] = self.stock_obj.tsdb[col_name].ewm(span=window).mean()
        self.stock_obj.tsdb['histogram'] = self.stock_obj.tsdb[col_name] - self.stock_obj.tsdb['ema']
        self.logger.info(f'{self.stock_obj.symbol.upper()}: EMA calculated')

    def _calc_normalized_ema(self):

        window   = self.ema_config['window']

        h = self.stock_obj.tsdb['histogram']
        self.stock_obj.tsdb['hist_norm'] = (h - h.min()) / (h.max() - h.min())
        self.stock_obj.tsdb['ema_norm'] = self.stock_obj.tsdb['hist_norm'].ewm(span=window).mean()
        self.logger.info(f'{self.stock_obj.symbol.upper()}: Normalized EMA calculated')

    def _calc_signal_basic_ema(self):
        '''
        Buy signal is when price crosses above EMA. Sell signal is when price crosses below EMA.
        This will create +1/-1 for buy/sell when raw_signal is diff'd.
        Crazy simple and worthless signal.
        '''
        col_name = self.stock_obj.config['data_map']['column_name']

        raw_signal = np.where(self.stock_obj.tsdb['ema'] > self.stock_obj.tsdb[col_name], 1.0, 0.0)
        self.stock_obj.tsdb['signal'] = raw_signal
        self.stock_obj.tsdb['signal'] = self.stock_obj.tsdb['signal'].diff()
        self.logger.info(f'{self.stock_obj.symbol.upper()}: Basic EMA signal generated')

    def _calc_signal_stupid_ema(self):
        '''
        Buy signal when hist_norm >= 0.7.  Sell signal when hist_norm <= 0.3. This is a stupid signal.
        '''
        col_name = self.stock_obj.config['data_map']['column_name']

        raw_signal = np.where(self.stock_obj.tsdb['hist_norm'] >= 0.6, 1.0, 0.0)
        raw_signal = np.where(self.stock_obj.tsdb['hist_norm'] <= 0.4, -1.0, 0.0)
        self.stock_obj.tsdb['signal'] = raw_signal
        self.stock_obj.tsdb['signal'] = self.stock_obj.tsdb['signal'].diff()
        self.logger.info(f'{self.stock_obj.symbol.upper()}: Stupid EMA signal generated')

