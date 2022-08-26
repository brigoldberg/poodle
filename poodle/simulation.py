# simulation.py

import math
import toml
from .utils import read_config
from .applogger import get_logger

class Simulation:
    """
    Step thru each price tick in a stock_obj and perform the following:
      - Determine if there is a buy/sell signal
      - Calculate existing risk on current position and determine size of risk
        desired to be added or removed from current position.
      - Trade stock and update book and log trade.
    """
    def __init__(self, stock_obj):

        self.stock_obj = stock_obj

        log_level = self.stock_obj.config['logging']['log_level']
        self.col_name = self.stock_obj.config['data_map']['column_name']
        self.risk_limit = self.stock_obj.config['strategy']['max_position_risk']
        self.logger = get_logger(f'sim-{self.stock_obj.symbol}', log_level)

        self._paper_trade()

    def _buy_risk_check(self, trade_date):
        '''
        Input: trade_date -- Return: Shares allowed to be purchased.
        If held position > risk_limit, do not add to position. Else, add shares.
        shares_to_buy = (risk_limit - book_value)/spot_price. '''

        risk_envelope = self.risk_limit - self.stock_obj.get_book_value(trade_date)
        if risk_envelope <= 50:
            # too close to envelope, allow zero shares to trade
            self.logger.info(f'{trade_date}:{self.stock_obj.symbol} Failed risk check')
            return 0    
        else:
            shares = math.floor(risk_envelope / self.stock_obj.tsdb[self.col_name].loc[trade_date])
            self.logger.info(f'{trade_date}:{self.stock_obj.symbol} Passed risk check. Allow {shares} shares')
            return shares

    def _paper_trade(self):
        '''
        signal check -> risk check -> get trade size -> log trade
        '''
        symbol = self.stock_obj.symbol

        for trade_date in self.stock_obj.signal.index:

            spot_price  = self.stock_obj.tsdb[self.col_name].loc[trade_date]
            signal = self.stock_obj.signal.loc[trade_date]

            if signal >= 0.9:       # Buy signal
                buy_quant = _buy_risk_check(trade_date)
                if buy_quant >= 1:
                    self.stock_obj.log_trade(trade_date, buy_quant, spot_price)

            elif signal <= -0.9:    # Sell signal
                sell_quant = self.stock_obj.get_shares_held(trade_date) * -1
                self.stock_obj.log_trade(trade_date, sell_quant, spot_price)

