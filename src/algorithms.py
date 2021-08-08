from datetime import datetime
import time
import src.utils as utils

class Algorithm():
    def __init__(self, ticker, account_balance, calculateSMA, buy, sell, getCurrentPrice):
        self.calculateSMA, self.buy, self.sell, self.getCurrentPrice, self.ticker, self.acct_balance = \
            calculateSMA, buy, sell, getCurrentPrice, ticker, account_balance

    # Can be called at the end of the daemon to get final balance
    def sell_all(self):
        # Get the current price of the ticker
        currPrice = self.getCurrentPrice(self.ticker)
        if (currPrice == -1):
            return -1
        return self.sell(self.ticker, self.num_coins, currPrice)

# Day trading cryptocurrency algorithm. This method will begin closely monitoring the coin if
# the current price of the coin is down 3% below the 1 day SMA. It will then buy the coin if
# an upswing is happening. It will then sell the coin if the price is percent_drop_from_high
# below the highest price reached while monitoring, if a 10% profit is made, or if losses hit 4%.
class HighFreqTrading(Algorithm):
    def __init__(self, ticker, acct_balance, calculateSMA, buy, sell, getCurrentPrice):
        super().__init__(ticker, acct_balance, calculateSMA, buy, sell, getCurrentPrice)
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

        sma_4hr = self.calculateSMA(self.ticker, 0.15)
        sma1 = self.calculateSMA(self.ticker, 1)
        sma15 = self.calculateSMA(self.ticker, 15)

        if ((not self.monitor_buy and not self.monitor_sell) and (currPrice <= (0.97) * sma1)):
            self.monitor_buy = True
            self.low_value = currPrice
            utils.writelog(f"Monitoring {self.ticker} to buy.")

        elif (self.monitor_buy):
            if (currPrice < self.low_value):
                self.low_value = currPrice

            if (currPrice > (1.01) * self.low_value and sma_4hr > sma1):
                self.to_buy = True

        elif (self.monitor_sell):
            # record highest value reached
            if (currPrice > self.high_value):
                self.high_value = currPrice

            if (currPrice >= (1.05) * self.bought_at):
                percent_drop_from_high = 0.997

            #    minimize losses to 4% max             sell if price is dropping past the high we reached            # sell if we make 10% profit
            if (currPrice <= (0.96) * self.bought_at or (currPrice <= (percent_drop_from_high) * self.high_value and currPrice > (1.015) * self.bought_at)):   
                self.to_sell = True

        # If buy condition is set, purchase as much coin as possible
        if (self.to_buy):
            if (self.acct_balance >= currPrice):
                self.num_coins = self.buy(self.ticker, self.acct_balance, currPrice)
                self.acct_balance = 0
                self.bought_at = currPrice
                self.high_value = currPrice
            self.to_buy = False
            self.monitor_buy = False
            self.monitor_sell = True 

        # If sell condition is set, sell all coins
        elif (self.to_sell):
            self.acct_balance += self.sell(self.ticker, self.num_coins, currPrice)
            utils.writelog(f"balance is at ${acct_balance}\n")
            self.num_coins = 0
            self.bought_at = 0
            self.to_sell = False
            self.monitor_sell = False