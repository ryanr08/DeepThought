from datetime import datetime
import utils as utils
import coinbase_api as cb
import algorithms as alg
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import sys
import warnings

class BackTest:
    def __init__(self, df):
        self.df = df
        self.index = int(0.85 * len(df))

    def calculate_sma(self, coin_id, n_days):
        sma = 0
        j = 0
        while (j <= n_days * 24 and (self.index + j) < len(self.df)):
            sma += float(self.df.close[self.index + j])
            j += 24
        return sma / n_days

    def get_current_price(self, coin_id):
        price = float(self.df.close[self.index])
        self.index -= 1
        return price

def obtain_crypto_dataset(ticker):
    data = []
    i = 4
    while(i < 5000):
        start_days_prior = i
        num_days = 4
        data += cb.getHistoricalData(ticker, start_days_prior, num_days)
        if (len(data) <= 1):
            utils.writelog(f"Error obtaining historical data. response = {data}", True)
            print(i)
            break
        i += 4
    df = pd.DataFrame(data, columns=[ "time", "low", "high", "open", "close", "volume" ])
    df.to_csv(f"../datasets/{ticker}.csv", mode='a')
    return df

def plot_test_results(ticker, df, buy_and_sell_points):
    plt.locator_params(axis="x", nbins=4)
    plt.locator_params(axis="y", nbins=4)
    plt.xlabel("Time")
    plt.ylabel("Price in Dollars")
    plt.plot(df.time, df.close)
    plt.title(f"{ticker} price over time.")
    warnings.filterwarnings("ignore")
    plt.axes().set_xticklabels([utils.epoch_time_to_human(x) for x in plt.axes().get_xticks()])
    plt.axes().set_yticklabels(['$' + str(y) for y in plt.axes().get_yticks()])
    for point in buy_and_sell_points:
        (action, (time, price)) = point
        plt.annotate(action, (time, price))
    plt.savefig(f"{ticker}-test-results.png", figsize=(10, 10), dpi=100)

def main():
    if (len(sys.argv) != 2):
        print(f"Error with arguments. \nUsage:\n{sys.argv[0]} <ticker>")
        sys.exit()
    ticker = sys.argv[1]
    try:
        df = pd.read_csv(f"../datasets/{ticker}.csv")
    except:
        df = obtain_crypto_dataset(ticker)

    test = BackTest(df)
    balance = 100
    utils.writelog(f"Running backtesting on {ticker}...\n", True)
    # Get the algorithm that we want to test on
    algorithm = alg.basicTrading(ticker, balance, test.calculate_sma, utils.buy, utils.sell, test.get_current_price, test=True)
    buy_and_sell_points = []
    while(test.index >= 10):
        action, price = algorithm.run()
        if (action != ""):
            buy_and_sell_points += tuple([(action, tuple((test.df.time[test.index], price)))])

    buy_and_sell_points += tuple([('S', tuple((test.df.time[test.index], float(df.close[test.index]))))])
    # Get test stats
    acct_balance = algorithm.sell_all() + algorithm.acct_balance
    percent_gain = 100 * (acct_balance - balance) / balance
    final_balance_if_held = (balance / df.close[int(0.85 * len(df))]) * df.close[0]
    percent_gain_if_held = round((100 * (final_balance_if_held - balance) / balance), 0)
    utils.writelog(f"\nTest on {ticker} complete!\nFinal Balance: ${round(acct_balance, 2)}\nPercent gain: {round(percent_gain, 0)}%\nFinal Balance if held: ${round(final_balance_if_held, 2)}\nPercent gain if held: {percent_gain_if_held}%\n", True)

    plot_test_results(ticker, df, buy_and_sell_points)     # plot results

if __name__ == "__main__":
    main()