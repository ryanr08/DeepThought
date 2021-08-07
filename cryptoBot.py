import src.coinbase_api as cbase
import src.algorithms as alg
import time
from datetime import datetime

ticker = "ADA-USD"

def writelog(input):
    l = open("orders.log", "a")
    l.write(input)
    l.close()

def main():
    acct_balance = 100000 # Amount in dollars of available paper money
    num_coins : float = 0
    bought_at : float = 0  # Last price we bought at
    to_buy = False
    to_sell = False
    monitor_buy = False
    monitor_sell = False
    high_value = 0   # Highest value reached while we held
    low_value = 0     # Lowest value in dip we see

    # Daemon
    counter = 0
    while (counter < 25000):
        # Run calculations every 5 seconds.
        time.sleep(5)
        counter += 1    # Stops cryptobot from running after a certain amount of time.

        # Get the current price of the ticker
        currPrice = cbase.getCurrentPrice(ticker)
        if (currPrice == -1):
            continue

    currPrice, acct_balance, monitor_sell, monitor_buy, high_value, bought_at, to_buy, to_sell, num_coins = \
           alg.high_frequency_trading_alg(currPrice, acct_balance, monitor_sell, monitor_buy, high_value, bought_at, to_buy, to_sell, num_coins)
    
    acct_balance, num_coins = alg.sell(currPrice, acct_balance, num_coins)
    writelog(str(datetime.now()))
    writelog(f"FINAL BALANCE: {acct_balance} + '\n")

if __name__ == "__main__":
    main()