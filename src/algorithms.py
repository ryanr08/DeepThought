import src.coinbase_api as cbase
from datetime import datetime
import time

ticker = "ADA-USD"

def writelog(input):
    l = open("orders.log", "a")
    l.write(input)
    l.close()

# Buy a coin with paper money
def purchase(currentPrice, balance, coins_held):
    balance = balance * 0.995
    coins_held = balance / currentPrice
    balance = 0
    writelog(str(datetime.now()) + '\n')
    print(f"BUY {coins_held} {ticker} at ${currentPrice} each")
    writelog(f"BUY {coins_held} {ticker} at ${currentPrice} each\n\n")
    return balance, coins_held

# Sell a coin for paper money
def sell(currentPrice, balance, coins_held):
    balance = coins_held * currentPrice
    writelog(str(datetime.now()) + '\n')
    print(f"SELL ALL {ticker} at ${currentPrice} each")
    writelog(f"SELL ALL {ticker} at ${currentPrice} each\n")
    writelog(f"balance is at ${balance}\n\n")
    return balance * (0.995), coins_held

# This is for day trading cryptocurrencies. This method will monitor the coin if
# the current price of the coin is down 3% below the 1 day SMA. It will then buy the coin if
# an upswing is happening. It will then sell the coin if the price is percent_drop_from_high
# below the highest price reached while monitoring, if a 10% profit is made, or if losses hit 4%.
#
#
# In order to run this function in the daemon, it must be called as so:
#
# currPrice, acct_balance, monitor_sell, monitor_buy, high_value, bought_at, to_buy, to_sell = \
#           high_frequency_trading_alg(currPrice, acct_balance, monitor_sell, monitor_buy, high_value, bought_at, to_buy, to_sell)
#
#
def high_frequency_trading_alg(currPrice, acct_balance, monitor_sell, monitor_buy, high_value, bought_at, to_buy, to_sell, num_coins):
    percent_drop_from_high = 0.98   # Price below high to sell at
    sma_4hr = cbase.calculateSMA(ticker, 0.15)
    sma1 = cbase.calculateSMA(ticker, 1)
    sma15 = cbase.calculateSMA(ticker, 15)

    if ((not monitor_buy and not monitor_sell) and (currPrice <= (0.97) * sma1)):
        monitor_buy = True
        low_value = currPrice

    if (monitor_buy):
        if (currPrice < low_value):
            low_value = currPrice
                                            
        if (currPrice > (1.01) * low_value and sma_4hr > sma1):
            to_buy = True

    if (monitor_sell):
        # record highest value reached
        if (currPrice > high_value):
            high_value = currPrice

        if (currPrice >= (1.05) * bought_at):
            percent_drop_from_high = 0.997

        #    minimize losses to 4% max             sell if price is dropping past the high we reached            # sell if we make 10% profit
        if (currPrice <= (0.96) * bought_at or (currPrice <= (percent_drop_from_high) * high_value and currPrice > (1.015) * bought_at)):   
            to_sell = True
        
    # If buy condition is set, purchase as much coin as possible
    if (to_buy):
        if (acct_balance >= currPrice):
            acct_balance, num_coins = purchase(currPrice, acct_balance, num_coins)
            bought_at = currPrice
            high_value = currPrice
        to_buy = False
        monitor_buy = False
        monitor_sell = True 

    # If sell condition is set, sell all coins
    elif (to_sell):
        acct_balance, num_coins = sell(currPrice, acct_balance, num_coins)
        bought_at = 0
        to_sell = False
        monitor_sell = False
    
    return currPrice, acct_balance, monitor_sell, monitor_buy, high_value, bought_at, to_buy, to_sell, num_coins