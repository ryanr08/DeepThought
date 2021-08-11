# DeepThought

DeepThought is a cryptocurrency trading bot. 
It interfaces with Coinbase Pro's API and attempts to make 
financially profitable trades.

## Set Up and Installation

### 1. Create a CoinbasePro account along with an API key. 

### 2. Install dependencies
```
pip install -r requirements.txt
```

### 3. Initialize API key
Set up either environment variables for 'COINBASE_API', 'COINBASE_SECRET', and 'COINBASE_PASS', or a file in the root named key.txt which contains each of those variables on a seperate line in the listed order.

## Usage

### Run cryptoBot.py

```
nohup python3 cryptobot.py <ticker> &
```

You can change the balance value and the algorithm in the code and watch as you make fake money!

### Backtesting

Run backtest.py:
```
python3 backtest.py <ticker>
```

You can configure the algorithm in the code and test it on any ticker's historical data!

## Contributing

Feel free to fork the repository and mess around with it! 
Also definitely make pull requests if you believe you have some good contributions!
You can also check out the issues and work on one of those if you desire.
