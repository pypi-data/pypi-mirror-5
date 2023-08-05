"""
(c) 2013 Tsung-Han Yang
This source code is released under the Apache license.  
blacksburg98@yahoo.com
Created on April 1, 2013
"""
import datetime as dt
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates 
import finpy.fpdateutil as du
import finpy.fpcommon as fpcmn
import utils as ut

class Equity(pd.DataFrame):
    """
    Equity is something that will be/was/is in the Portfolio.
    buy is either a NaN, or a floating number. 
    If buy is a floating number, then we buy the number of shares of the equity.
    sell is either a NaN, or a floating number.
    shares is the daily balance of the equities.
    """
    def __init__(self, data=None, index=None, columns=None, dtype=None, copy=False, init_share=0.0):
        if columns == None:
            cols = ['open', 'high', 'low', 'close', 'volume', 'actual_close', 'buy',
            'sell', 'shares']
        else:
            cols = columns
        pd.DataFrame.__init__(self, data=data, index=index, columns=cols, dtype=dtype, copy=copy)
        self['shares'][0] = init_share
        self['buy'] = 0.0
        self['sell'] = 0.0

    def buy(self, date, shares, price, ldt_timestamps):
        self.fillna_shares(date, ldt_timestamps)
        self['buy'][date] = shares
        self['shares'][date] += shares

    def sell(self, date, shares, price, ldt_timestamps):
        self.fillna_shares(date, ldt_timestamps)
        self['sell'][date] = shares
        self['shares'][date] -= shares
        return price*shares

    def fillna_shares(self, date, ldt_timestamps):
        last_valid = self['shares'].last_valid_index()
        self['shares'][last_valid:date] = self['shares'][last_valid]

    def dailyrtn(self):
        """
        Return the return of each day, a list.
        """
        daily_rtn = []
        ldt_timestamps = self.index
        for date in range(len(ldt_timestamps)):
            if date == 0:
                daily_rtn.append(0)
            else:
             daily_rtn.append((self['close'][date]/self['close'][date-1])-1)
        return np.array(daily_rtn)

    def nml_close(self):
        return self['close']/self['close'].ix[0]
    def avg_dailyrtn(self): 
        return np.average(self.dailyrtn())

    def std(self):
        return np.std(self.dailyrtn())

    def sharpe(self, k=252):
        """
        Return Sharpe Ratio. 
        You can overwirte the coefficient with k.
        The default is 252.
        """
        return np.sqrt(k) * self.avg_dailyrtn()/self.std()

    def sortino(self, k=252):
        """
        Return Sortino Ratio. 
        You can overwirte the coefficient with k.
        The default is 252.
        """
        daily_rtn = self.dailyrtn()
        negative_daily_rtn = daily_rtn[daily_rtn < 0]
        sortino_dev = np.std( negative_daily_rtn)
        sortino = (self.avg_dailyrtn() / sortino_dev) * np.sqrt(k)
        return sortino

    def totalrtn(self):
        return self['close'][-1]/self['close'][0]

    def moving_average(self, tick, window=20, nml=False):
        """
        Return an array of moving average. Window specified how many days in
        a window.
        """
        mi = self.bollinger_band(tick=tick, window=window, nml=nml, mi_only=True)
        return mi

    def bollinger_band(self, tick, window=20, k=2, mi_only=False):
        """
        Return four arrays for Bollinger Band.
        The first one is the moving average.
        The second one is the upper band.
        The thrid one is the lower band.
        The fourth one is the Bollinger value.
        If mi_only, then return the moving average only.
        """
        ldt_timestamps = self.index
        pre_timestamps = fpcmn.pre_timestamps(ldt_timestamps, window)
        # ldf_data has the data prior to our current interest.
        # This is used to calculate moving average for the first window.
        ldf_data = ut.get_tickdata([tick], pre_timestamps)
        merged_data = pd.concat([ldf_data[tick]['close'], self['close']])
        bo = dict()
        bo['mi'] = pd.rolling_mean(merged_data, window=window)[ldt_timestamps] 
        if mi_only:
            return bo['mi']
        else:
            sigma = pd.rolling_std(merged_data, window=window)
            bo['hi'] = bo['mi'] + k * sigma[ldt_timestamps] 
            bo['lo'] = bo['mi'] - k * sigma[ldt_timestamps] 
            bo['ba'] = (merged_data[ldt_timestamps] - bo['mi']) / (k * sigma[ldt_timestamps])
            return bo

    def beta_alpha(self, market):
        """
        market is a Equity representing the market. 
        It can be S&P 500, Russel 2000, or your choice of market indicator.
        """
        beta, alpha = np.polyfit(market["close"], self["close"], 1)
        return beta, alpha

    def drawdown(self, tick, window=10):
        """
        Find the peak within the retrospective window.
        Drawdown is the difference between the peak and the current value.
        """
        ldt_timestamps = self.index
        pre_timestamps = fpcmn.pre_timestamps(ldt_timestamps, window)
        # ldf_data has the data prior to our current interest.
        # This is used to calculate moving average for the first window.
        ldf_data = ut.get_tickdata([tick], pre_timestamps)
        merged_data = pd.concat([ldf_data[tick]['close'], self['close']])
        total_timestamps = merged_data.index
        dd = pd.Series(index=ldt_timestamps)
        j = 0
        for i in range(len(pre_timestamps), len(total_timestamps)):
            win_start = total_timestamps[i - window]
            win_end = total_timestamps[i]
            ts_value = merged_data[win_start:win_end]
            current = merged_data[win_end]
            peak = np.amax(ts_value)
            dd[j] = (peak-current)/peak
            j += 1
        return dd

    def current_ratio(self, st_date, end_date):
        return (self['close'][end_date]/self['close'][st_date])
