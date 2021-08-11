from datetime import datetime
import time

def writelog(input, test=False):
    print(input)
    if (not test):
        log_path = __file__[:__file__.rindex('/')] + "/../orders.log"
        log = open(log_path, "a")
        log.write(input + '\n')
        log.close()
    else:
        log_path = __file__[:__file__.rindex('/')] + "/backtest.log"
        log = open(log_path, "a")
        log.write(input + '\n')
        log.close()

# Buy a coin with paper money
def buy(coin_id, amount, current_price, test=False):
    amount *= 0.995
    coins_held = round(amount / current_price, 3)
    balance = 0
    if(not test):
        writelog(str(datetime.now()))
    writelog(f"BUY {coins_held} {coin_id} at ${current_price} each.\n", test)
    return coins_held

# Sell a coin for paper money
def sell(coin_id, coin_amt, current_price, test=False):
    balance = round(coin_amt * current_price, 3)
    if (coin_amt > 0):
        if(not test):
            writelog(str(datetime.now()))
        writelog(f"SELL ALL {coin_id} at ${current_price} each.", test)
        return balance * (0.995)
    else:
        return -1

def epoch_time_to_human(timestamp):
    return time.strftime("%b %Y", time.localtime(timestamp))