# simulation.py
import locale
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

        #self._paper_trade()
    
    def _risk_check(self, signal, trade_date):

        existing_position_risk = self.stock_obj.get_book_value(trade_date)
        risk_allowed = self.risk_limit - abs(existing_position_risk)
        #self.logger.info(f'Existing position risk {self.stock_obj.symbol.upper()}:${locale.format_string("%.2f", existing_position_risk)}')
        self.logger.info(f'{self.stock_obj.symbol.upper()}  Allowed risk: ${locale.format_string("%.2f", risk_allowed)}')
        
        if signal == 'buy' and risk_allowed > 0:
            trade_size = self._calc_trade_size(risk_allowed, trade_date)
            self.logger.info(f'Buy {self.stock_obj.symbol.upper()} {trade_size} shares.')
            return trade_size

        elif signal == 'sell':
            # dump entire position
            trade_size = self.stock_obj.trade_log.shares.loc[:trade_date].sum()
            self.logger.info(f'Sell {self.stock_obj.symbol.upper()} {trade_size} shares.')
            return trade_size

        else:
            self.logger.error(f'No signal {self.stock_obj.symbol.upper()}')
            
        return 0
            


    def _calc_trade_size(self, risk_allowed, trade_date):
        
        spot_price = self.stock_obj.tsdb[self.col_name].loc[trade_date]
        return math.floor(risk_allowed / spot_price)
        
        """
        risk_envelope = self.risk_limit - self.stock_obj.get_book_value(trade_date)
        if risk_envelope <= 50:
            # too close to envelope, allow zero shares to trade
            self.logger.info(f'{trade_date}:{self.stock_obj.symbol} Failed risk check')
            return 0    
        else:
            shares = math.floor(risk_envelope / self.stock_obj.tsdb[self.col_name].loc[trade_date])
            self.logger.info(f'{trade_date}:{self.stock_obj.symbol} Passed risk check. Allow {shares} shares')
            return shares
        """
    
    def _paper_trade(self):
        ''' signal check -> risk check -> get trade size -> log trade '''
        symbol = self.stock_obj.symbol

        for trade_date in self.stock_obj.signal.index:

            if signal >= 0.9:       # Buy signal
                trade_shares = _risk_check('buy', trade_date)

            elif signal <= -0.9:    # Sell signal
                trade_shares = _risk_check('sell', trade_date)



