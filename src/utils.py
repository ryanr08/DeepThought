from datetime import datetime

def writelog(input):
    print(input)
    log = open("orders.log", "a")
    log.write(input + '\n')
    log.close()

# Buy a coin with paper money
def buy(coin_id, amount, current_price):
    amount *= 0.995
    coins_held = round(amount / current_price, 3)
    balance = 0
    writelog(str(datetime.now()))
    writelog(f"BUY {coins_held} {coin_id} at ${current_price} each.\n")
    return coins_held

# Sell a coin for paper money
def sell(coin_id, coin_amt, current_price):
    if (coin_amt > 0):
        balance = round(coin_amt * current_price, 3)
        writelog(str(datetime.now()))
        writelog(f"SELL ALL {coin_id} at ${current_price} each.")
        return balance * (0.995)
    else:
        return 0