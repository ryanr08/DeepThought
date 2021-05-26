import json, hmac, hashlib, time, base64, requests, sys, pytz, os
from requests.auth import AuthBase
from datetime import datetime, timedelta

# Create custom authentication for Exchange
class CoinbaseExchangeAuth(AuthBase):
    def __init__(self, api_key, secret_key, passphrase):
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase

    def __call__(self, request):
        timestamp = str(time.time())
        message = timestamp + request.method + request.path_url + (request.body or b'').decode()
        hmac_key = base64.b64decode(self.secret_key)
        signature = hmac.new(hmac_key, message.encode(), hashlib.sha256)
        signature_b64 = base64.b64encode(signature.digest()).decode()

        request.headers.update({
            'CB-ACCESS-SIGN': signature_b64,
            'CB-ACCESS-TIMESTAMP': timestamp,
            'CB-ACCESS-KEY': self.api_key,
            'CB-ACCESS-PASSPHRASE': self.passphrase,
            'Content-Type': 'application/json'
        })
        return request

# Load in API key data from system environment variables

API_KEY = os.environ.get('COINBASE_API')
API_SECRET = os.environ.get('COINBASE_SECRET')
API_PASS = os.environ.get('COINBASE_PASS')

if(None in [API_KEY,API_SECRET,API_PASS]):
    try:
        f = open("key.txt", "r")

        API_KEY = str(f.readline())[0:-1]
        API_SECRET = str(f.readline())[0:-1]
        API_PASS = str(f.readline())

        f.close()
    except:
        print("Please set up your API key in key.txt or in your enviornment variables.\nSet your key.txt file as:\nAPI_KEY\nAPI_SECRET\nAPI_PASS")
        sys.exit(1)

# set up timezone
timezone = pytz.timezone('US/Pacific')

# set up authentication with API key
api_url = 'https://api.pro.coinbase.com/'
auth = CoinbaseExchangeAuth(API_KEY, API_SECRET,  API_PASS)

# Calculate a simple moving average for a given coin over n_days
def calculateSMA(coin_id, n_days):
    # get historical data
    granularity = 0
    if (n_days >= 150):
        granularity = 86400
    elif (n_days >= 12):
        granularity = 21600
    elif (n_days > 3):
        granularity = 3600
    elif (n_days > 1):
        granularity = 900
    elif (n_days > 0.2):
        granularity = 300
    else:
        granularity = 60

    # get ISO time of right now and time of n_days ago
    today = datetime.now(tz=timezone).isoformat()
    n_days_ago = (datetime.now(tz=timezone) - timedelta(hours=24*n_days)).isoformat()

    # set up parameters for API
    params = {
        'start': str(n_days_ago),
        'end': str(today),
        'granularity': granularity
    }

    res = requests.get(api_url + f'products/{coin_id}/candles' + "?start=" + str(params['start']) + "&end=" + str(params['end']) + "&granularity=" + str(params['granularity']), auth=auth)

    # calculate sma based off close values
    sum = 0
    count = 0
    sma = 0
    for i in range(len(res.json())):
        count = count + 1
        sum = sum + res.json()[i][3]
    sma = sum / count
    return sma

# Get the current market price of a specific coin
def getCurrentPrice(coin_id):
    try:
        r = requests.get(api_url + f'products/{coin_id}/ticker', auth=auth).json()['price']
        return float(r)
    except:
        print("ERROR getting values from API")
        return -1


# Get account information
def getAccountInfo():
    r = requests.get(api_url + 'accounts', auth=auth)
    return r.json()

# Place a buy order, amount in dollars
def place_limit_buy(coin_id, amount):   
    
    currPrice = getCurrentPrice(coin_id)
    num_tokens = amount // currPrice

    order = {
        'type': 'limit',
        'size': num_tokens,
        'price': currPrice,
        'side': 'buy',
        'product_id': coin_id,
    }
    r = requests.post(api_url + 'orders', json=order, auth=auth)
    return r.json(), amount, num_tokens

# Place a sell order for coin_amt of a given coin_id 
def place_limit_sell(coin_id, coin_amt):

    currPrice = getCurrentPrice(coin_id)

    order = {
        'type': 'limit',
        'size': coin_amt,
        'price': currPrice,
        'side': 'sell',
        'product_id': coin_id,
    }
    r = requests.post(api_url + 'orders', json=order, auth=auth)
    return r.json()

# get the price from num_mins ago
def getPreviousPrice(coin_id, num_mins):
    
    n_mins_ago = (datetime.now(tz=timezone) - timedelta(minutes=num_mins)).isoformat()

    # set up parameters for API
    params = {
        'start': str(n_mins_ago),
        'end': str(datetime.now(tz=timezone).isoformat()),
        'granularity': 60
    }

    res = requests.get(api_url + f'products/{coin_id}/candles' + "?start=" + str(params['start']) + "&end=" + str(params['end']) + "&granularity=" + str(params['granularity']), auth=auth)
    return (res.json()[-1][3])

# get average price from num_mins ago till now
def getPreviousPriceAvg(coin_id, num_mins):
    sum = 0
    for i in range(1, num_mins):
        sum += getPreviousPrice(coin_id, i)
    return sum / num_mins

