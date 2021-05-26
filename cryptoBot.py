import coinbase_api as cbase
import time
from datetime import datetime

ticker = "FIL-USD"
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
    return balance * (99.3), coins_held

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
    percent_drop_from_high = 0.99

    # Daemon
    while (counter < 25000):
        time.sleep(5)
        counter += 1
        currPrice = cbase.getCurrentPrice(ticker)
        if (currPrice == -1):
            continue

        sma2 = cbase.calculateSMA(ticker, 2)
        sma15 = cbase.calculateSMA(ticker, 15)

        if ((not monitor_buy and not monitor_sell) and (currPrice <= (0.97) * sma2 or sma2 < (.98) * sma15)):
            monitor_buy = True
            low_value = currPrice

        if (monitor_buy):
            if (currPrice < low_value):
                low_value = currPrice
                                                #and
            if (currPrice > (1.01) * low_value or currPrice > cbase.getPreviousPriceAvg(ticker, 5)):
                to_buy = True

        if (monitor_sell):
            # record highest value reached
            if (currPrice > high_value):
                high_value = currPrice

            if (currPrice >= (1.08) * bought_at):
                percent_drop_from_high = 0.995

            #    minimize losses to 3% max             sell if price is dropping past the high we reached            # sell if we make 5% profit
            if (currPrice <= (0.97) * bought_at or (currPrice <= (percent_drop_from_high) * high_value and currPrice > (1.03) * bought_at)):   
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