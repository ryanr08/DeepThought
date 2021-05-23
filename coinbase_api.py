import json, hmac, hashlib, time, base64, requests
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

# Load in API key data from key.txt located in the current directory
try:
    f = open("key.txt", "r")

    API_KEY = str(f.readline())[0:-1]
    API_SECRET = str(f.readline())[0:-1]
    API_PASS = str(f.readline())

    f.close()
except:
    print("Please set up your API key in key.txt.\nSet your key.txt file as:\nAPI_KEY\nAPI_SECRET\nAPI_PASS")

# set up authentication with API key
api_url = 'https://api.pro.coinbase.com/'
auth = CoinbaseExchangeAuth(API_KEY, API_SECRET,  API_PASS)

# Calculate a simple moving average for a given coin over n_days
def calculateSMA(coin_id, n_days):
    # get historical data
    today = datetime.now().isoformat()
    n_days_ago = (datetime.now() - timedelta(days=n_days)).isoformat()

    params = {
        'start': str(n_days_ago),
        'end': str(today),
        'granularity': 300 #86400
    }

    res = requests.get(api_url + f'products/{coin_id}/candles' + "?start=" + str(params['start']) + "&end=" + str(params['end']) + "&granularity=" + str(params['granularity']), auth=auth)
    #print(res.json())
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
    # getting 24hr stats
    try:
        r = requests.get(api_url + f'products/{coin_id}/stats', auth=auth).json()['last']
        return float(r)

    except:
        print("ERROR getting values from API")
        exit(1)


# Get account information
def getAccountInfo():
    r = requests.get(api_url + 'accounts', auth=auth)
    return r.json()

#Place an order
def Buy(coin_id):   
    order = {
        'size': 1.0,
        'price': 1.0,
        'side': 'buy',
        'product_id': coin_id,
    }
    r = requests.post(api_url + 'orders', json=order, auth=auth)
    return r.json()

# getting single product data
# r = requests.get(api_url + 'products/BTC-USD', auth=auth)
# print(r.json())