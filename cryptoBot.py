import coinbase_api as cbase
import time
from datetime import datetime

ticker = "ADA-USD"

# write to the log file
def writelog(input):
    l = open("log.txt", "a")
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
    writelog(f"balance is at ${balance}\n")
    return balance, coins_held


def sell(currentPrice, balance, coins_held):
    while(coins_held > 0):
        coins_held -= 1
        balance += currentPrice
    writelog(str(datetime.now()) + '\n')
    print(f"SELL ALL {ticker} at ${currentPrice} each")
    writelog(f"SELL ALL {ticker} at ${currentPrice} each\n")
    writelog(f"balance is at ${balance}\n")
    return balance, coins_held

def main():

    counter = 0
    currPrice = 0
    sleep_time = 5 # number of seconds to wait each iteration
    BALANCE = 100000 # Amount in dollars of available paper money
    COINS_HELD = 0

    bought_at = 0  # last price we bought at
    buy = False
    sell = False
    monitor = False

    # Daemon
    while (counter < 17280):
        time.sleep(sleep_time)
        counter += 1
        currPrice = cbase.getCurrentPrice(ticker)
        sma = cbase.calculateSMA(ticker, 1)

        if (currPrice <= (0.95) * sma):
            buy = True

        if (bought_at != 0 and (currPrice > (1.01) * bought_at or currPrice <= (0.98) * bought_at)):
            sell = True

        if (buy):
            if (BALANCE >= currPrice):
                BALANCE, COINS_HELD = purchase(currPrice, BALANCE, COINS_HELD)
                bought_at = currPrice
            buy = False
        elif (sell):
            if (COINS_HELD > 0):
                BALANCE, COINS_HELD = sell(currPrice, BALANCE, COINS_HELD)
                bought_at = 0
            sell = False


    BALANCE, COINS_HELD = sell(currPrice, BALANCE, COINS_HELD)
    writelog(str(datetime.now()))
    writelog(f"FINAL BALANCE: {BALANCE} + '\n")

if __name__ == "__main__":
    main()