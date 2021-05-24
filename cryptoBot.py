import coinbase_api as cbase
import time
from datetime import datetime

ticker = "ETH-USD"

# write to the log file
def writelog(input):
    l = open("orders.log", "a")
    l.write(input)
    l.close()

def purchase(currentPrice, balance, coins_held):
    num_purchased = 0
    while (balance >= currentPrice):
        coins_held += 1
        balance -= currentPrice
        num_purchased += 1
    writelog(str(datetime.now()) + '\n')
    print(f"BUY {num_purchased} {ticker} at ${currentPrice} each")
    writelog(f"BUY {num_purchased} {ticker} at ${currentPrice} each\n")
    writelog(f"balance is at ${balance}\n\n")
    return balance, coins_held


def sell(currentPrice, balance, coins_held):
    while(coins_held > 0):
        coins_held -= 1
        balance += currentPrice
    writelog(str(datetime.now()) + '\n')
    print(f"SELL ALL {ticker} at ${currentPrice} each")
    writelog(f"SELL ALL {ticker} at ${currentPrice} each\n")
    writelog(f"balance is at ${balance}\n\n")
    return balance, coins_held

def main():

    counter = 0
    currPrice = 0
    sleep_time = 5 # number of seconds to wait each iteration
    acct_balance = 100000 # Amount in dollars of available paper money
    num_coins : int = 0

    bought_at : int = 0  # last price we bought at
    to_buy = False
    to_sell = False
    monitor_buy = False
    monitor_sell = False
    high_value = 0   # highest value reached while we held
    low_value = 0     # lowest value in dip we see


    # Daemon
    while (counter < 17280):
        time.sleep(sleep_time)
        counter += 1
        currPrice = cbase.getCurrentPrice(ticker)
        sma = cbase.calculateSMA(ticker, 5)

        if ((not monitor_buy and not monitor_sell) and currPrice <= (0.95) * sma):
            monitor_buy = True
            low_value = currPrice

        if (monitor_buy):
            if (currPrice < low_value):
                low_value = currPrice

            if (currPrice > (1.01) * low_value and currPrice > cbase.getPreviousPrice(ticker, 1)):
                to_buy = True

        if (monitor_sell):
            if (currPrice > high_value):   # set highest value reached
                high_value = currPrice

            if (currPrice <= (0.95) * bought_at or (currPrice <= (0.98) * high_value and currPrice > bought_at) or currPrice >= (1.05) * bought_at):   # minimize losses to 2% max/ sell if price is dropping past the high we reached
                to_sell = True
            

        if (to_buy):
            if (acct_balance >= currPrice):
                acct_balance, num_coins = purchase(currPrice, acct_balance, num_coins)
                bought_at = currPrice
            to_buy = False
            monitor_buy = False
            monitor_sell = True
            if (currPrice >= high_value):
                high_value = currPrice

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