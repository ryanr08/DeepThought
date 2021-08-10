from datetime import datetime
import utils as utils
import coinbase_api as cb
import algorithms as alg
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

ticker = 'XLM-USD'

class BackTest:
    def __init__(self, df):
        self.df = df
        self.index = len(df) - 500

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
    while(i < 1000):
        start_days_prior = i
        num_days = 4
        data += cb.getHistoricalData(ticker, start_days_prior, num_days)
        if (len(data) <= 0):
            utils.writelog(f"Error obtaining historical data. response = {data}")
            print(i)
            break
        i += 4
    df = pd.DataFrame(data, columns=[ "time", "low", "high", "open", "close", "volume" ])
    df.to_csv(f"../datasets/{ticker}.csv", mode='a')
    return df

def plot_coin_price(ticker, df):
    plt.locator_params(axis="x", nbins=4)
    plt.locator_params(axis="y", nbins=4)
    plt.xlabel("Time")
    plt.ylabel("Price")
    plt.plot(df.time, df.close)
    plt.title(f"{ticker} price over time.")
    import warnings
    warnings.filterwarnings("ignore")
    plt.axes().set_xticklabels([utils.epoch_time_to_human(x) for x in plt.axes().get_xticks()])

def main():
    try:
        df = pd.read_csv(f"../datasets/{ticker}.csv")
    except:
        df = obtain_crypto_dataset(ticker)
    
    test = BackTest(df)
    balance = 100

    utils.writelog(f"Running backtesting on {ticker}...")
    high_frequency_algorithm = alg.HighFreqTrading(ticker, balance, test.calculate_sma, utils.buy, utils.sell, test.get_current_price)

    for i in range(len(df) - 600):
        high_frequency_algorithm.run()

    # Get test stats
    acct_balance = high_frequency_algorithm.sell_all() + high_frequency_algorithm.acct_balance
    percent_gain = 100 * (acct_balance - balance) / balance
    final_balance_if_held = (balance / df.close[len(df) - 1]) * df.close[0]
    percent_gain_if_held = round((100 * (final_balance_if_held - balance) / balance), 0)
    utils.writelog(f"Test complete!\nFinal Balance: ${round(acct_balance, 2)}\nPercent gain: {round(percent_gain, 0)}%\nFinal Balance if held: ${round(final_balance_if_held, 2)}\nPercent gain if held: {percent_gain_if_held}%\n")

if __name__ == "__main__":
    main()