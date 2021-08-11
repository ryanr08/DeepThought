from datetime import datetime
import time
import utils as utils

class Algorithm():
    def __init__(self, ticker, account_balance, calculateSMA, buy, sell, getCurrentPrice, test=False):
        self.calculateSMA, self.buy, self.sell, self.getCurrentPrice, self.ticker, self.acct_balance, self.test = \
            calculateSMA, buy, sell, getCurrentPrice, ticker, account_balance, test

    # Can be called at the end of the daemon to get final balance
    def sell_all(self):
        # Get the current price of the ticker
        currPrice = self.getCurrentPrice(self.ticker)
        if (currPrice == -1):
            return -1
        if (self.num_coins > 0):
            return self.sell(self.ticker, self.num_coins, currPrice, self.test)
        else:
            return 0

# Sample trading algorithm that employs DMAC (Double Moving Average Crossover) analysis.
# This algorithm will buy the coin when the short term SMA crosses under the long term SMA 
# and then it will sell the coin when the short term SMA is much greater than the long term SMA.
class basicTrading(Algorithm):
    def __init__(self, ticker, acct_balance, calculateSMA, buy, sell, getCurrentPrice, test=False):
        super().__init__(ticker, acct_balance, calculateSMA, buy, sell, getCurrentPrice, test)
        self.num_coins : float = 0
        self.holding = False
    
    def run(self):
        # Get the current price of the ticker
        currPrice = self.getCurrentPrice(self.ticker)
        if (currPrice == -1):
            return
        
        # calculate short term and long term sma
        sma3 = self.calculateSMA(self.ticker, 3)    # short term
        sma50 = self.calculateSMA(self.ticker, 50)  # long term
        sma25 = self.calculateSMA(self.ticker, 25)

        # if short term sma < long term, buy
        if (not self.holding and sma3 < sma50):
            self.num_coins = self.buy(self.ticker, self.acct_balance, currPrice, self.test)
            self.acct_balance = 0
            self.holding = True
            if (self.test):
                return "B", currPrice
        
        # if short term sma is much greater than long term, sell
        if (self.holding and currPrice > sma50 * 1.05 and sma3 < sma50):
            self.acct_balance += self.sell(self.ticker, self.num_coins, currPrice, self.test)
            utils.writelog(f"balance is at ${round(self.acct_balance, 2)}\n", self.test)
            self.num_coins = 0
            self.holding = False
            if (self.test):
                return "S", currPrice
        return "", 0

# High frequency trading cryptocurrency algorithm. This method will begin closely monitoring the coin
# if the current price of the coin is down below the 50 day SMA. It will then buy the coin if
# an upswing is happening. It will then sell the coin if the price is percent_drop_from_high
# below the highest price reached while monitoring and the short term sma is below the long term.
class HighFreqTrading(Algorithm):
    def __init__(self, ticker, acct_balance, calculateSMA, buy, sell, getCurrentPrice, test=False):
        super().__init__(ticker, acct_balance, calculateSMA, buy, sell, getCurrentPrice, test)
        self.bought_at : float = 0  # Last price we bought at
        self.to_buy = False         # Set if algorithm is going to buy
        self.to_sell = False        # Set if algorithm is going to sell
        self.monitor_buy = False    # When set true, begin monitoring for a good time to buy
        self.monitor_sell = False   # Set true after buying, monitoring for when to sell
        self.high_value = 0         # Highest value reached while we held
        self.low_value = 0          # Lowest value in dip we see
        self.num_coins : float = 0  # Number of coins held

    def run(self):
        percent_drop_from_high = 0.98   # Price below high to sell at

        # Get the current price of the ticker
        currPrice = self.getCurrentPrice(self.ticker)
        if (currPrice == -1):
            return

        #sma_4hr = self.calculateSMA(self.ticker, 0.15)
        sma3 = self.calculateSMA(self.ticker, 3)
        sma50 = self.calculateSMA(self.ticker, 50)

        if (self.bought_at == 0 and not self.monitor_buy and (currPrice < (0.98) * sma50) and sma3 > sma50):
            self.monitor_buy = True
            self.low_value = currPrice
            utils.writelog(f"Monitoring {self.ticker} to buy.", self.test)

        if (self.monitor_buy):
            if (currPrice < self.low_value):
                self.low_value = currPrice

            if (currPrice > (1.01) * self.low_value and sma3 < sma50):
                self.to_buy = True
                self.monitor_buy = False

        if (self.monitor_sell):
            # record highest value reached
            if (currPrice > self.high_value):
                self.high_value = currPrice

            if (currPrice >= (1.05) * self.bought_at):
                percent_drop_from_high = 0.96

            #    minimize losses to 10% max
            if (currPrice <= (0.90) * self.bought_at or (currPrice <= (percent_drop_from_high) * self.high_value and sma3 < sma50)):   
                self.to_sell = True
                self.monitor_sell = False

        # If buy condition is set, purchase as much coin as possible
        if (self.to_buy):
            self.num_coins = self.buy(self.ticker, self.acct_balance, currPrice, self.test)
            self.acct_balance = 0
            self.bought_at = currPrice
            self.high_value = currPrice
            self.to_buy = False
            self.monitor_sell = True
            if (self.test):
                return "B", currPrice

        # If sell condition is set, sell all coins
        if (self.to_sell):
            self.acct_balance += self.sell(self.ticker, self.num_coins, currPrice, self.test)
            utils.writelog(f"balance is at ${round(self.acct_balance, 2)}\n", self.test)
            self.num_coins = 0
            self.bought_at = 0
            self.to_sell = False
            if (self.test):
                return "S", currPrice
        return "", 0
