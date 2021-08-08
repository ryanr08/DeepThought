import src.coinbase_api as cb
import src.algorithms as alg
import time
from datetime import datetime
import src.utils as utils

def main():
    ticker = "XLM-USD"
    acct_balance = 1000000 # Amount in dollars of available paper money

    high_frequency_algorithm = alg.HighFreqTrading(ticker, acct_balance, cb.calculateSMA, utils.buy, utils.sell, cb.getCurrentPrice)

    # Daemon
    utils.writelog(f"CryptoBot has started and is actively tracking {ticker}.")
    counter = 0
    while (counter < 51840):
        counter += 1    # Stops cryptobot from running after 72 hours.
        # Run trading algorithm
        high_frequency_algorithm.run()
        # Run calculations every 5 seconds.
        time.sleep(5)

    # Get final balance
    acct_balance = high_frequency_algorithm.sell_all()
    utils.writelog(str(datetime.now()))
    utils.writelog(f"FINAL BALANCE: {acct_balance} + '\n\n")

if __name__ == "__main__":
    main()