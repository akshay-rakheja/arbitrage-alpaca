## What is a DEX?

A Decentralized exchange or a DEX is a peer-to-peer marketplace that facilitates transactions in a permission-less manner. DEX's use "Automated Market Maker" protocols that orchestrate trade without the need for a centralized body.

## What is a DEX Aggregator?

A DEX Aggregator (eg: 1Inch) aims to provide the best prices for swaps across multiple liquidity sources (eg: Uniswap, Sushiswap, etc). Using a DEX aggregator like 1Inch helps us avoid relying on a single source for price data. This is important since 1 liquidity source alone might not be able to route the entire transaction without experiencing significant slippage.

## What is a CEX?

A Centralized exchange or CEX is operated in a centralized manner by a company. Orders on a CEX are maintained in an order book where buyers and sellers place their bids and a trade executes when the bids match.

## What are we building?

We are building an arbitrage bot that trades when the price of an asset is different on a Centralized exchange compared to that on a Decentralized exchange by a given percentage. You can find the source code of the bot [here.](https://github.com/akshay-rakheja/arbitrage-alpaca/blob/master/dex_cex_arb.py)

This will involve:
1. Receiving quotes from a CEX and DEX asynchronously every 5 seconds
2. Checking if those prices meet the arbitrage condition
3. Executing trades if the condition is met
4. Rebalancing position on both sides if needed

We will be using [Alpaca's Crypto API's](https://alpaca.markets/docs/api-references/) to get quotes and execute trades on Centralized exchanges such as FTXUS and Coinbase. On the other hand, 1Inch's API will help us get quotes and execute trades on a Decentralized exchanges like Quickswap and Uniswap. 

We will be using Polygon network (formerly Matic Network)  to execute our trades on a decentralized exchange. The two main reasons for this are its transaction costs and speed. It costs a few cents (single digits) to execute a swap trade on Polygon while it can cost tens of dollars on Ethereum to do the same task. This will help us maximize our profits by keeping transaction costs minimal. (Note: the bot is not keeping into account the transaction costs accrued by trading on Polygon since they are quite minimal). 

Since we will be executing the trades on the Polygon network, it makes sense to trade one of the most liquid assets on it, 'MATIC'. 'MATIC' is the base currency for the network and is required to pay for all the transaction costs on the network. Similarly, for the Centralized exchanges, we will use Alpaca's Market Data and Trading API to execute trade on the 'MATICUSD' pair.

### Rough idea of our Arbitrage strategy

We will try to execute a version of Convergence Arbitrage strategy. This strategy involves a long/short trade. Here, the bot buys the crypto on the exchange where it is underpriced ("long") and sells it on the exchange where it is overpriced ("short"). When the two prices are not deviating far enough anymore we can reverse the trades we did earlier and sell on the exchange where we went long and vice versa.


## Let's BUIDL

Since the code is a little lengthy I will break it into snippets and explain them along the way. So, Let's get started!

```
import requests
import logging
import json
from web3 import Web3
import config
import logging
import asyncio


# ENABLE LOGGING - options, DEBUG,INFO, WARNING?
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

```

In the snippet above, we are importing the necessary libraries and enabling logging. Logging will keep us informed on the prices and the arbitrage condition. 
Then, we define a few variables that will control our arbitrage logic and quotes.

```
# Flag if set to True, will execute live trades
production = False

# Permissible slippage
slippage = 1

# Seconds to wait between each quote request
waitTime = 5

# Minimum percentage between prices to trigger arbitrage
min_arb_percent = 0.5
```
`production` is like a safety flag that should be set to True only if you are ready to send transactions with your bot and False otherwise.  `slippage` is the maximum amount of slippage that we would like when executing a trade on the DEX aggregator. `waitTime` as the name suggests is the amount of seconds we would like to wait before requesting quotes from our CEX and DEX sources. `min_arb_percent` is the minimum percentage difference we would like between the quotes to consider an arbitrage condition. Essentially, if the quotes from two sources are not at least as far apart as this percentage, then there is no arbitrage. Keep in mind, keeping  `min_arb_percent` value high might lead to fewer chances of the arbitrage condition being triggered. While keeping it too low may lead to more frequent trades and a net loss due to transaction costs and slippage on the decentralized side of things.

Now let's define the API parameters for both the sources (CEX and DEX).

```
# OneInch API
BASE_URL = 'https://api.1inch.io/v4.0/137'

# if MATIC --> USDC - (enter the amount in units Ether)
trade_size = 10
amount_to_exchange = Web3.toWei(trade_size, 'ether')

matic_address = Web3.toChecksumAddress(
    '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE')  # MATIC Token Contract address on Polygon Network

usdc_address = Web3.toChecksumAddress(
    '0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174')  # USDC Token contract address on Polygon Network

# Contract abi for usdc contract on polygon
usdc_contract_abi = json.load(open('usdc_contract_abi.json', 'r'))


eth_provider_url = <Your WEB3 RPC URL>
base_account = Web3.toChecksumAddress(<Your Wallet address>)
wallet_address = base_account
private_key = <Private key for your wallet (eg: Metamask)>
```
First, let's go over the 1Inch API parameters and relevant Web3 variables defined above. We define a `BASE_URL` for the API that stays constant for all the requests to 1Inch. 
`trade_size` is the amount of `MATIC` token we would like to trade. This should be at least 10 and should increment by 10. This is because Alpaca only lets you trade MATIC in multiples of 10. Then, we take the trade_size and convert it into 10 MATIC. We do this using the Web3 library that we imported earlier. `ether` is used merely as a unit in `Web3.toWei(trade_size, 'ether')` to represent MATIC as a token with 18 decimal places. You can read more on that [here.](https://ethereum.stackexchange.com/questions/38704/why-most-erc-20-tokens-have-18-decimals) 
Next, we initialize the contract addresses for the tokens we intend on trading, MATIC and USDC. You can find the contract addresses for these tokens on [polygonscan.com](https://polygonscan.com/tokens). Keep in mind that these addresses will be different on different chains/networks.
You will see that we are importing something called 'usdc_contract_abi'. This is the contract ABI for the USDC token. Later, we will be using this to check our USDC balance in our wallet. You can find the ABI [here.](https://polygonscan.com/address/0x2791bca1f2de4661ed88a30c99a7a9449aa84174#code)
Next, we will initialize our `eth_provider_url`, `base_account` and `private_key`. Provider URL is an HTTP address that you can get from a node api provider like [Alchemy](https://alchemy.com/?r=fbf1a4db9748e301). Base Account is your Wallet Address (eg: Metamask) which should start something like (0X...) and the private key as the name suggests is the corresponding private key to your wallet. Your private key should be kept secret as anyone with access to your private key has access to all your assets in the wallet.

Now that we have discussed the API parameters and variables relevant to the decentralized side of things, let's take a look at the centralized side. 
```
# Alpaca API
BASE_ALPACA_URL = 'https://paper-api.alpaca.markets'
DATA_URL = 'https://data.alpaca.markets'
HEADERS = {'APCA-API-KEY-ID': <YOUR ALPACA KEY ID>,
           'APCA-API-SECRET-KEY': <YOUR ALPACA SECRET KEY>}

trading_pair = 'MATICUSD'  # Checking quotes and trading MATIC against USD
exchange = 'FTXU'  # FTXUS

last_alpaca_ask_price = 0
last_oneInch_market_price = 0
alpaca_trade_counter = 0
oneInch_trade_counter = 0
```
The above snippet initializes the key parameters we will be using to make API calls through Alpaca. `BASE_ALPACA_URL` is used to access the trading api's that Alpaca provides. You might notice that this url has its value set to `https://paper-api.alpaca.markets`. This gets you access to a paper trading account once you register with Alpaca. It is always a good idea to try a new strategy using a paper trading account first. Once you are confident enough to trade with real money, this url can be changed to `https://api.alpaca.markets`.
We will be using `DATA_URL` to get the latest quote for our trading pair. To complete a request to Alpaca we need to define its headers in a JSON format (dictionary in python). This information needs to be kept secret since anyone with access to your KeyID and Secret Key can access your Alpaca account.
As we did earlier, we need to define what token we are trading. In Alpaca's case it is `MATICUSD`. This is token MATIC trading against US dollars. Then, we initialize the exchange we would like the quotes from. Here it is initialized to FTX US `FTXU`. You can change this based on the asset you are trading and its liquidity on that exchange. Alpaca makes our life better by making their [API docs](https://alpaca.markets/docs/api-references/market-data-api/) super easy to follow. 
Finally, we initialize the variables `last_alpaca_ask_price`, `last_oneInch_market_price`, `alpaca_trade_counter` and `oneInch_trade_counter` to 0. The last two are used to check if we need to rebalance our positions.

Now that we have initialized `eth_provider_url` and imported the Web3 library, we are ready to establish a connection to blockchain. 

```
def connect_to_ETH_provider():
    try:
        web3 = Web3(Web3.HTTPProvider(eth_provider_url))
    except Exception as e:
        logger.warning(
            "There is an issue with your initial connection to Ethereum Provider: {0}".format(e))
        quit()
    return web3

# establish web3 connection
w3 = connect_to_ETH_provider()
```

`connect_to_ETH_provider()` uses the method `HTTPProvider()` from `web3` with `eth_provider_url` as a parameter to establish a connection with the blockchain. `w3` is an instance of the Polygon node that is returned when we establish this connection. 
Remember to use the provider url for Polygon chain since transaction costs are minimal. 

```
async def main():
    '''
    These are examples of different functions in the script.
    Uncomment the command you want to run.
    '''
    # Accessing the usdc contract on polygon using Web3 Library
    usdc_token = w3.eth.contract(address=usdc_address, abi=usdc_contract_abi)
    # Log the current balance of the usdc token for our wallet_address
    usdc_balance = usdc_token.functions.balanceOf(wallet_address).call()

    # Log the current balance of the MATIC token in our Alpaca account
    logger.info('Matic Position on Alpaca: {0}'.format(get_positions()))
    # Log the current Cash Balance (USD) in our Alpaca account
    logger.info("USD position on Alpaca: {0}".format(
        get_account_details()['cash']))
    # Log the current balance of MATIC token in our wallet_address
    logger.info('Matic Position on 1 Inch: {0}'.format(
        Web3.fromWei(w3.eth.getBalance(wallet_address), 'ether')))
    # Log the current balance of USDC token in our wallet_address.     
    logger.info('USD Position on 1 Inch: 
        {0}'.format(usdc_balance/10**6))

    while True:
        l1 = loop.create_task(get_oneInch_quote_data(
            matic_address, usdc_address, amount_to_exchange))
        l2 = loop.create_task(get_Alpaca_quote_data(trading_pair, exchange))
        # Wait for the tasks to finish
        await asyncio.wait([l1, l2])
        check_arbitrage()
        # Wait for the a certain amount of time between each quote request
        await asyncio.sleep(waitTime)
```

The above snippet is our main function. It runs asynchronously (starts with async) and essentially logs a bunch of stuff. The comments above the `logger` statements explain what we are trying to log. So, Let's start with the `while True` loop. 
We are trying to create two asynchronous tasks (`l1` and `l2`) that fetch quotes from 1Inch and Alpaca respectively for our asset MATIC. In the case of 1Inch, we pass in the contract addresses of both the tokens MATIC and USDC along with the amount we intend to swap in case we would like to make a trade if an arbitrage situation arrives. Then, we use `asyncio.wait()` to wait for both the tasks to finish. This is important because we would like to receive the quotes from both the sources before we decide what to do next. Our next step is to check if we meet any arbitrage condition and wait a certain amount of time (we set it as 5 seconds, remember?) using `asyncio.sleep(waitTime)`. Then, we begin logging the price quotes from 1inch and Alpaca and repeat the process every 5 seconds.

Now let's look at some of the functions we called in main.

```
def get_positions():
    '''
    Get positions
    '''
    try:
        positions = requests.get(
            '{0}/v2/positions'.format(BASE_ALPACA_URL), headers=HEADERS)
        # logger.info('Alpaca positions reply status code: {0}'.format(
        # positions.status_code))
        if positions.status_code != 200:
            logger.info(
                "Undesirable response from Alpaca! {}".format(positions.json()))
            return False
        # positions = positions[0]
        matic_position = positions.json()[0]['qty']
        # logger.info('Matic Position on Alpaca: {0}'.format(matic_position))
    except Exception as e:
        logger.exception(
            "There was an issue getting positions from Alpaca: {0}".format(e))
        return False
    return matic_position

```
We use `get_positions()` to get our current `MATIC` position on Alpaca. We use a `GET` request  with `/v2/positions` endpoint to retrieve our position. The `qty` attribute of the JSON response gives you your MATIC position.

```
async def get_oneInch_quote_data(_from_coin, _to_coin, _amount_to_exchange):
    '''
    Get trade quote data from 1Inch API
    '''
    # Try to get a quote from 1Inch
    try:
        # Get the current quote response for the trading pair (MATIC/USDC)
        quote = requests.get(
            '{0}/quote?fromTokenAddress={1}&toTokenAddress={2}&amount={3}'.format(BASE_URL, _from_coin, _to_coin, _amount_to_exchange))
        # Status code 200 means the request was successful
        if quote.status_code != 200:
            logger.info(
                "Undesirable response from 1 Inch! This is probably bad.")
            return False
        # Refer to the global variable we initialized earlier
        global last_oneInch_market_price
        # Get the current quoted price from the quote response in terms USDC (US Dollar)
        last_oneInch_market_price = int(quote.json()['toTokenAmount'])/10**6
        # Log the current quote of MATIC/USDC
        logger.info('OneInch Price for 10 MATIC: {0}'.format(
            last_oneInch_market_price))
    # If there is an error, log it
    except Exception as e:
        logger.exception(
            "There was an issue getting trade quote from 1 Inch: {0}".format(e))
        return False

    return last_oneInch_market_price
```
The function in the above snippet is responsible for getting quotes from our decentralized exchange aggregator 1Inch. You can read more about their API endpoints [here](https://docs.1inch.io/docs/aggregation-protocol/api/swagger).
I hope the comments in the snippet above try to be as clear as possible but let's try to understand what's happening here. Basically, we are trying to get the latest quote using 1Inch API by passing it the required query params. Along the way, we try to log our response for better understanding of the quotes and if any error arises during runtime. Then, we convert the query response to a dollar denominated value by dividing it by 10^6. This is because unlike other ERC-20 tokens, USDC only has 6 decimals of precision. 
Fun fact: Another famous stable coin, USDT also has 6 decimals of precision.

Next, we will look at the function that gets us quotes using Alpaca's API. 

```
async def get_Alpaca_quote_data(trading_pair, exchange):
    '''
    Get trade quote data from Alpaca API
    '''
    # Try to get a quote from 1Inch
    try:
        # Get the current quote response for the trading pair (MATIC/USDC)
        quote = requests.get(
            '{0}/v1beta1/crypto/{1}/quotes/latest?exchange={2}'.format(DATA_URL, trading_pair, exchange), headers=HEADERS)
        # Status code 200 means the request was successful
        if quote.status_code != 200:
            logger.info(
                "Undesirable response from Alpaca! {}".format(quote.json()))
            return False
        # Refer to the global variable we initialized earlier
        global last_alpaca_ask_price
        # Get the latest quoted asking price from the quote response in terms US Dollar
        last_alpaca_ask_price = quote.json(
        )['quote']['ap'] * 10  # for 10 MATIC
        # Log the latest quote of MATICUSD
        logger.info('Alpaca Price for 10 MATIC: {0}'.format(
            last_alpaca_ask_price))
    # If there is an error, log it
    except Exception as e:
        logger.exception(
            "There was an issue getting trade quote from Alpaca: {0}".format(e))
        return False

    return last_alpaca_ask_price
```
The function in the above snippet helps us in getting quotes from our centralized exchange provider Alpaca. You can read more about their API endpoints [here](https://alpaca.markets/docs/api-references/market-data-api/crypto-pricing-data/historical/).
The comments in the snippet above are pretty self explanatory so I won't go in detail. Basically, we are trying to get the latest asking price of MATIC in terms of US dollars from FTX US using Alpaca's Crypto API. We pass it the required query params. Then, we access the dollar denominated value and multiply it by 10 to get the dollar denominated asking price for 10 MATIC tokens since 10 is our default trading size. 
Next, we will look at the function that checks if any arbitrage opportunity is present.

```
def check_arbitrage():
    logger.info('Checking for arbitrage opportunities')
    rebalance = needs_rebalancing()
    # if the current price at alpaca is greater than the current price at 1inch by a given arb % and we do not need a rebalance
    # then we have an arbitrage opportunity. In this case we will buy on 1Inch and sell on Alpaca
    if (last_alpaca_ask_price > last_oneInch_market_price * (1 + min_arb_percent/100) and rebalance != True):
        logger.info('Selling on ALPACA, Buying on 1Inch')
        if production:
            sell_order = post_Alpaca_order(
                trading_pair, trade_size, 'sell', 'market', 'gtc')
            # if the above sell order goes through we will subtract 1 from alpaca trade counter
            if sell_order['status'] == 'accepted':
                global alpaca_trade_counter
                alpaca_trade_counter -= 1
                # Only buy on oneInch if our sell txn on alpaca goes through
                # To buy 10 MATIC, we multiply its price by 10 (amount to exchange) and then further multiply it by 10^6 to get USDC value
                buy_order_data = get_oneInch_swap_data(
                    usdc_address, matic_address, last_oneInch_market_price*amount_of_usdc_to_trade)
                buy_order = signAndSendTransaction(buy_order_data)
                if buy_order == True:
                    global oneInch_trade_counter
                    oneInch_trade_counter += 1
    # If the current price at alpaca is less than the current price at 1inch by a given arb % and we do not need a rebalance
    # then we have an arbitrage opportunity. In this case we will buy on Alpaca and sell on 1Inch
    elif (last_alpaca_ask_price < last_oneInch_market_price * (1 - min_arb_percent/100) and rebalance != True):
        logger.info('Buying on ALPACA, Selling on 1Inch')
        if production:
            buy_order = post_Alpaca_order(
                trading_pair, 10, 'buy', 'market', 'gtc')
            # if the above buy order goes through we will add 1 to alpaca trade counter
            if buy_order['status'] == 'accepted':
                global alpaca_trade_counter
                alpaca_trade_counter += 1
                # Only sell on oneInch if our buy txn on alpaca goes through
                # To sell 10 MATIC, we pass it amount to exchnage
                sell_order_data = get_oneInch_swap_data(
                    matic_address, usdc_address, amount_to_exchange)
                sell_order = signAndSendTransaction(sell_order_data)
                if sell_order == True:
                    global oneInch_trade_counter
                    oneInch_trade_counter -= 1
    # If neither of the above conditions are met then either there is no arbitrage opportunity found and/or we need to rebalance
    else:
        if rebalance:
            rebalancing()
        else:
            logger.info('No arbitrage opportunity available')
```
The code above seems a bit daunting at first but as we walk through it you will realize it's executing very simple operations. There are a few variables that we need to understand first. We went over both the trade counters (`alpaca_trade_counter` and `oneInch_trade_counter`) earlier in the post. They are initialized to 0 when the bot starts and increment or decrement by 1 for Alpaca and 1Inch based on the trade executed. A "sell" trade decrements the counter by 1 while a "buy" trade increments it by 1. `rebalance` is a variable that takes the value returned by `needs_rebalancing`. It essentially checks if our positions need rebalancing before we proceed with our next trade and even consider an arbitrage opportunity. We will go over the `needs_rebalancing` function later in the post. 
 `production` as we discussed earlier is a safety flag.
In this function, we look at 2 conditions to consider an arbitrage, the price difference between the two sources (Alpaca and 1Inch) and  whether our positions need rebalancing. Based on these conditions we decide whether we would like to buy/sell or rebalance our portfolio.

Next, let's take a look at the `needs_rebalancing()` function before we understand `rebalancing()`.

```
def needs_rebalancing():
    # Get current MATIC positions on both exchanges
    current_matic_alpaca = int(get_positions())
    current_matic_1Inch = int(Web3.fromWei(
        w3.eth.getBalance(wallet_address), 'ether'))
    # If the current amount of MATIC on either exchange minus the trade size (10) is greater than 0 then we are good enough to trade
    if current_matic_alpaca - 10 < 0 or current_matic_1Inch - 10 < 0:
        logger.info(
            'We will have less than 10 MATIC on one of the exchanges if we trade. We need to rebalance.')
        return True
    # If the current trade counter on Alpaca or 1Inch is not 0 then we need to rebalance
    if alpaca_trade_counter != 0 or oneInch_trade_counter != 0:
        logger.info("We need to rebalance our positions")
        return True
    return False
```

This function involves a couple of checks that return `True` if we need to rebalance our positions and `False` otherwise. 
Condition 1: If we have less than 10 MATIC on either of the exchanges that means we either have an active open position or we have less funds. 
Condition 2: If the trade counter for either of the exchanges is not 0 then we need to rebalance. Since we are going long/short at the same time on the exchanges, we need to reverse our positions before we execute on the next opportunity. 

```
def rebalancing():
    logger.info('Rebalancing')
    global alpaca_trade_counter
    global oneInch_trade_counter

    # Get current MATIC positions on both exchanges
    current_matic_alpaca = get_positions()
    current_matic_1Inch = Web3.fromWei(
        w3.eth.getBalance(wallet_address), 'ether')
    # Only execute rebalancing trades if production is true (we are live)
    if production:
        if (current_matic_alpaca - 10 > 0 and alpaca_trade_counter != 0):
            if alpaca_trade_counter > 0:
                logger.info('Rebalancing Alpaca side by selling on Alpaca')
                sell_order = post_Alpaca_order(
                    trading_pair, 10, 'sell', 'market', 'gtc')
                if sell_order['status'] == 'accepted':
                    alpaca_trade_counter -= 1
            else:
                logger.info('Rebalancing Alpaca side by buying on Alpaca')
                buy_order = post_Alpaca_order(
                    trading_pair, 10, 'buy', 'market', 'gtc')
                if buy_order['status'] == 'accepted':
                    alpaca_trade_counter += 1

        if current_matic_alpaca - 10 < 0 and alpaca_trade_counter != 0:
            logger.info(
                'Unable to rebalance Alpaca side due to insufficient funds')

        if current_matic_1Inch - 10 > 0 and oneInch_trade_counter != 0:
            if oneInch_trade_counter > 0:
                logger.info('Rebalancing oneInch side by selling on oneInch')
                sell_order_data = get_oneInch_swap_data(
                    matic_address, usdc_address, amount_to_exchange)
                sell_order = signAndSendTransaction(sell_order_data)
                if sell_order == True:
                    oneInch_trade_counter -= 1
            else:
                logger.info('Rebalancing oneInch side by buying on oneInch')
                buy_order_data = get_oneInch_swap_data(
                    matic_address, usdc_address, amount_to_exchange)
                buy_order = signAndSendTransaction(buy_order_data)
                if buy_order == True:
                    oneInch_trade_counter += 1
        if current_matic_1Inch - 10 < 0 and oneInch_trade_counter != 0:
            logger.info(
                'Unable to rebalance oneInch side due to insufficient funds')

```

The `rebalancing` function uses the amount of MATIC we hold on each exchange and their respective trade counters to determine if there needs to be a sell order or a buy order for that exchange. The trade counters for both the exchanges should either be `-1`,`0` or `1`. `-1` representing a short position on the exchange (Sell MATIC), `0` represents no active position and `1` represents a long position (Buy MATIC). If the trade counter on alpaca is greater than 0 that means a trade to buy alpaca had been executed earlier. We will need to sell this before we can make another trade again. Likewise, we will buy if the counter is less than 0. 
Functions `rebalancing()` , `needs_rebalancing()` and `check_arbitrage()` can be further optimized to maximize profits in my opinion, but they also serve as a good starting point for someone to looking to start trading on both the DeX's and CeX's simultaneously. 

Now that the core functions of the bot have been defined we can  call our main function.
```
loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()
```

Using asyncio library, we create an event loop and make it run until it finishes. In the loop we call our main function. Do remember though we defined it to work such that it runs indefinitely. So you will probably need to exit it by using `Ctrl+C`. Again, this can be improved upon to take inputs and exit a little more elegantly. 

Apart from the functions mentioned above, I have included some functions in the file that might help you interact with both the exchanges a little better. Let's briefly go over them. 
`get_account_details()` uses a `GET` request along with `/v2/account` endpoint to access your Alpaca account information. In this code we are just using it to access our cash balance. Apart from cash balance, you can use this endpoint to get a lot more important information about your account, such as buying power, portfolio value, account status, etc. That's great because 1 API call can get you so much information. 

`get_allowance()` method uses 1Inch's API endpoints to check how many tokens for a given token, 1Inch is allowed to spend from our address. By default, on Polygon network, 1Inch is allowed to spend an infinite amount of MATIC (since this is the native currency of the chain) but this is not the same for USDC tokens and it should most likely be 0 if you have not used 1Inch before. To approve 1Inch to spend your USDC tokens, we use the method `approve_ERC20()`. This method generates the necessary transaction data that approves 1Inch to spend a said token (USDC here) on your behalf. We need this because we would like 1Inch to find the best quotes for our trading pair `MATIC/USDC` and we need it to execute trade at those prices.
Once this transaction data has been created using `approve_ERC20()`, we can call `signAndSendTransaction()` to execute this approval. 

## Few takeaways:

1. Use Alpaca's APIs to access market data and instant trading capabilities if you are looking to trade crypto on centralized exchanges. They have most of the high volume popular coins and provide a super easy way to access information and execute trades.
2. Use 1Inch's APIs to receive quotes and trade in the cheapest way on the most popular EVM compatible blockchains. 
3. Logic for `check_arbitrage()`, `rebalancing()` and `needs_rebalancing()` is very naive in its approach and probably won't be profitable. But that shouldn't matter and discourage you. You can customize the logic as you wish. At the very least, it should give you a good starting point to trading using API's. 





