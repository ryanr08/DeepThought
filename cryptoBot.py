import coinbase_api as cbase
import time
from datetime import datetime

ticker = "ADA-USD"
def writelog(input):
    l = open("orders.log", "a")
    l.write(input)
    l.close()

def purchase(currentPrice, balance, coins_held):
    balance = balance * 0.995
    coins_held = balance / currentPrice
    balance = 0
    writelog(str(datetime.now()) + '\n')
    print(f"BUY {coins_held} {ticker} at ${currentPrice} each")
    writelog(f"BUY {coins_held} {ticker} at ${currentPrice} each\n\n")
    return balance, coins_held


def sell(currentPrice, balance, coins_held):
    balance = coins_held * currentPrice
    writelog(str(datetime.now()) + '\n')
    print(f"SELL ALL {ticker} at ${currentPrice} each")
    writelog(f"SELL ALL {ticker} at ${currentPrice} each\n")
    writelog(f"balance is at ${balance}\n\n")
    return balance * (0.995), coins_held

def main():

    counter = 0
    currPrice = 0
    sleep_time = 5 # number of seconds to wait each iteration
    acct_balance = 100000 # Amount in dollars of available paper money
    num_coins : float = 0

    bought_at : float = 0  # last price we bought at
    to_buy = False
    to_sell = False
    monitor_buy = False
    monitor_sell = False
    high_value = 0   # highest value reached while we held
    low_value = 0     # lowest value in dip we see
    percent_drop_from_high = 0.98

    # Daemon
    while (counter < 25000):
        time.sleep(5)
        counter += 1
        currPrice = cbase.getCurrentPrice(ticker)
        if (currPrice == -1):
            continue

        sma_4hr = cbase.calculateSMA(ticker, 0.15)
        sma1 = cbase.calculateSMA(ticker, 1)
        sma15 = cbase.calculateSMA(ticker, 15)

        if ((not monitor_buy and not monitor_sell) and (currPrice <= (0.97) * sma1 or sma1 < (.98) * sma15)):
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

            #    minimize losses to 4% max             sell if price is dropping past the high we reached            # sell if we make 5% profit
            if (currPrice <= (0.96) * bought_at or (currPrice <= (percent_drop_from_high) * high_value and currPrice > (1.015) * bought_at)):   
                to_sell = True
            

        if (to_buy):
            if (acct_balance >= currPrice):
                acct_balance, num_coins = purchase(currPrice, acct_balance, num_coins)
                bought_at = currPrice
                high_value = currPrice
            to_buy = False
            monitor_buy = False
            monitor_sell = True 

        elif (to_sell):
            acct_balance, num_coins = sell(currPrice, acct_balance, num_coins)
            bought_at = 0
            to_sell = False
            monitor_sell = False


    acct_balance, num_coins = sell(currPrice, acct_balance, num_coins)
    writelog(str(datetime.now()))
    writelog(f"FINAL BALANCE: {acct_balance} + '\n")

if __name__ == "__main__":
    main()