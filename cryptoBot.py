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

counterrr = 0
currPrice = 0
BALANCE = 100000
COINS_HELD = 0

# Daemon
while (counterrr < 7200):
    time.sleep(5)
    counterrr += 1
    currPrice = cbase.getCurrentPrice(ticker)
    sma200 = cbase.calculateSMA(ticker, 1)#calculateSMA(ticker, 200)
    if (currPrice < (sma200)):
        if (BALANCE >= currPrice):
            BALANCE, COINS_HELD = purchase(currPrice, BALANCE, COINS_HELD)
    elif (currPrice > (sma200)):
        if (COINS_HELD > 0):
            BALANCE, COINS_HELD = sell(currPrice, BALANCE, COINS_HELD)

BALANCE, COINS_HELD = sell(currPrice, BALANCE, COINS_HELD)
writelog(str(datetime.now()))
writelog(f"FINAL BALANCE: {BALANCE} + '\n")