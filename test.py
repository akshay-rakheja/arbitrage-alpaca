#!/usr/bin/env python
# -*- coding: utf-8 -*-

from cmath import log
import requests
import logging
import json
import os
from web3 import Web3
from wsgiref.headers import Headers
from alpaca_trade_api.rest import REST, TimeFrame
import config
import logging
from multiprocessing import Process
import time
import asyncio

# import web3


# ENABLE LOGGING - options, DEBUG,INFO, WARNING?
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

production = False  # False to prevent any public TX from being sent
slippage = 1
waitTime = 5

min_arb_percent = 0.5


# OneInch API
BASE_URL = 'https://api.1inch.io/v4.0/137'

# if MATIC --> USDC - (enter the amount in units Ether)
trade_size = 10
amount_to_exchange = Web3.toWei(trade_size, 'ether')

matic_address = Web3.toChecksumAddress(
    '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE')  # MATIC Token Contract address on Polygon Network


usdc_address = Web3.toChecksumAddress(
    '0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174')  # USDC Token contract address on Polygon Network

# Contract abi for usdc contract on poolygon
usdc_contract_abi = json.load(open('usdc_contract_abi.json', 'r'))


eth_provider_url = config.ALCHEMY_URL
base_account = Web3.toChecksumAddress(config.BASE_ACCOUNT)
wallet_address = base_account
private_key = config.PRIVATE_KEY


# Alpaca API
BASE_ALPACA_URL = 'https://paper-api.alpaca.markets'
DATA_URL = 'https://data.alpaca.markets'
HEADERS = {'APCA-API-KEY-ID': config.APCA_API_KEY_ID,
           'APCA-API-SECRET-KEY': config.APCA_API_SECRET_KEY}

trading_pair = 'MATICUSD'  # Checking quotes and trading MATIC against USD
exchange = 'FTXU'  # FTXUS

last_alpaca_ask_price = 0
last_oneInch_market_price = 0


async def main():
    '''
    These are examples of different functions in the script.
    Uncomment the command you want to run.
    '''
    # get price quote for 1 ETH in DAI right now
    # matic_price = one_inch_get_quote(
    #     ethereum, mcd_contract_address, Web3.toWei(1, 'ether'))
    usdc_token = w3.eth.contract(address=usdc_address, abi=usdc_contract_abi)
    usdc_balance = usdc_token.functions.balanceOf(wallet_address).call()

    logger.info('Matic Position on Alpaca: {0}'.format(get_positions()))
    logger.info("USD position on Alpaca: {0}".format(
        get_account_details()['cash']))
    logger.info('Matic Position on 1 Inch: {0}'.format(
        Web3.fromWei(w3.eth.getBalance(wallet_address), 'ether')))
    logger.info('USD Position on 1 Inch: {0}'.format(usdc_balance/10**6))

    while True:
        l1 = loop.create_task(get_oneInch_quote_data(
            matic_address, usdc_address, amount_to_exchange))
        l2 = loop.create_task(get_Alpaca_quote_data(trading_pair, exchange))
        # print(last_alpaca_ask_price)
        # Wait for the tasks to finish
        await asyncio.wait([l1, l2])
        check_arbitrage()
        # Wait for the a certain amount of time between each quote request
        await asyncio.sleep(waitTime)
    # print("matic price is :", matic_price['quote']['ap'])
    # time.sleep(2)
    # while True:
    #     matic_price_oneInch = get_oneInch_quote_data(
    #         matic_address, usdc_address, amount_to_exchange)
    #     print("matic price on OneInch is :", float(
    #         matic_price_oneInch['toTokenAmount'])/10**6, "USDC")
    #     matic_price_alpaca = get_Alpaca_quote_data(trading_pair, exchange)
    #     print("matic price on Alpaca is :", matic_price_alpaca['quote']['ap'])
    #     time.sleep(2)


async def get_oneInch_quote_data(_from_coin, _to_coin, _amount_to_exchange):
    '''
    Get trade quote data from 1Inch API
    '''
    try:
        quote = requests.get(
            '{0}/quote?fromTokenAddress={1}&toTokenAddress={2}&amount={3}'.format(BASE_URL, _from_coin, _to_coin, _amount_to_exchange))
        # logger.info('1inch quote reply status code: {0}'.format(
        # quote.status_code))
        # if quote.status_code != 200:
        # logger.info(
        #     "Undesirable response from 1 Inch! This is probably bad.")
        # return False
        global last_oneInch_market_price
        last_oneInch_market_price = int(quote.json()['toTokenAmount'])/10**6
        logger.info('OneInch Price for 10 MATIC: {0}'.format(
            last_oneInch_market_price))
    except Exception as e:
        logger.exception(
            "There was an issue getting trade quote from 1 Inch: {0}".format(e))
        return False

    return last_oneInch_market_price


async def get_Alpaca_quote_data(trading_pair, exchange):
    '''
    Get trade quote data from Alpaca API
    '''
    try:
        quote = requests.get(
            '{0}/v1beta1/crypto/{1}/quotes/latest?exchange={2}'.format(DATA_URL, trading_pair, exchange), headers=HEADERS)
        # logger.info('Alpaca quote reply status code: {0}'.format(
        # quote.status_code))
        # if quote.status_code != 200:
        #     logger.info(
        #         "Undesirable response from Alpaca! {}".format(quote.json()))
        #     return False
        global last_alpaca_ask_price
        last_alpaca_ask_price = quote.json(
        )['quote']['ap'] * 10  # for 10 MATIC
        logger.info('Alpaca Price for 10 MATIC: {0}'.format(
            last_alpaca_ask_price))
    except Exception as e:
        logger.exception(
            "There was an issue getting trade quote from Alpaca: {0}".format(e))
        return False

    return last_alpaca_ask_price


def get_oneInch_swap_data(_from_coin, _to_coin, _amount_to_exchange):
    '''
    Get call data from 1Inch API
    '''
    try:
        call_data = requests.get(
            '{0}/swap?fromTokenAddress={1}&toTokenAddress={2}&amount={3}&fromAddress={4}&slippage={5}'.format(BASE_URL, _from_coin, _to_coin, _amount_to_exchange, wallet_address, slippage))
        logger.info('response from 1 inch generic call_data request - status code: {0}'.format(
            call_data.status_code))
        if call_data.status_code != 200:
            logger.info(call_data.json()['description'])
            return False
        call_data = call_data.json()
        nonce = w3.eth.getTransactionCount(wallet_address)
        tx = {
            'from': call_data['tx']['from'],
            'nonce': nonce,
            'to': Web3.toChecksumAddress(call_data['tx']['to']),
            'chainId': 137,
            'value': int(call_data['tx']['value']),
            'gasPrice': w3.toWei(call_data['tx']['gasPrice'], 'wei'),
            'data': call_data['tx']['data'],
            'gas': call_data['tx']['gas']
        }
        # tx = call_data['tx']
        # tx['nonce'] = nonce  # Adding nonce to tx data

        # logger.info('get_api_call_data: {0}'.format(call_data))

    except Exception as e:
        logger.warning(
            "There was a issue getting get contract call data from 1 inch: {0}".format(e))
        return False

    return tx


def get_account_details():
    '''
    Get Alpaca Trading Account Details
    '''
    try:
        account = requests.get(
            '{0}/v2/account'.format(BASE_ALPACA_URL), headers=HEADERS)
        # logger.info('Alpaca account reply status code: {0}'.format(
        # account.status_code))
        if account.status_code != 200:
            # logger.info(
            #     "Undesirable response from Alpaca! {}".format(account.json()))
            return False
        # logger.info('get_account_details: {0}'.format(account.json()))
    except Exception as e:
        logger.exception(
            "There was an issue getting account details from Alpaca: {0}".format(e))
        return False
    return account.json()


def get_open_orders():
    '''
    Get open orders
    '''
    try:
        open_orders = requests.get(
            '{0}/v2/orders'.format(BASE_URL), headers=HEADERS)
        logger.info('Alpaca open orders reply status code: {0}'.format(
            open_orders.status_code))
        if open_orders.status_code != 200:
            logger.info(
                "Undesirable response from Alpaca! {}".format(open_orders.json()))
            return False
        logger.info('get_open_orders: {0}'.format(open_orders.json()))
    except Exception as e:
        logger.exception(
            "There was an issue getting open orders from Alpaca: {0}".format(e))
        return False
    return open_orders.json()


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


def post_Alpaca_order(symbol, qty, side, type, time_in_force):
    '''
    Post an order to Alpaca
    '''
    try:
        order = requests.post(
            '{0}/v2/orders'.format(BASE_ALPACA_URL), headers=HEADERS, json={
                'symbol': symbol,
                'qty': qty,
                'side': side,
                'type': type,
                'time_in_force': time_in_force,
            })
        logger.info('Alpaca order reply status code: {0}'.format(
            order.status_code))
        if order.status_code != 200:
            logger.info(
                "Undesirable response from Alpaca! {}".format(order.json()))
            return False
        # logger.info('post_Alpaca_order: {0}'.format(order.json()))
    except Exception as e:
        logger.exception(
            "There was an issue posting order to Alpaca: {0}".format(e))
        return False
    return order.json()


# Establish connection to the WEB3 provider
def connect_to_ETH_provider():
    try:
        web3 = Web3(Web3.HTTPProvider(eth_provider_url))
    except Exception as e:
        logger.warning(
            "There is an issue with your initial connection to Ethereum Provider: {0}".format(e))
        quit()
    return web3


# Sign and send txns to the blockchain
def signAndSendTransaction(transaction_data):
    try:
        txn = w3.eth.account.signTransaction(transaction_data, private_key)
        tx_hash = w3.eth.sendRawTransaction(txn.rawTransaction)
        logger.info(
            'TXN can be found at https://polygonscan.com/tx/{0}'.format(Web3.toHex(tx_hash)))
    except Exception as e:
        logger.warning(
            "There is an issue sending transaction to the blockchain: {0}".format(e))
    return tx_hash

# Check for Arbitrage opportunities


def check_arbitrage():
    logger.info('Checking for arbitrage opportunities')
    # print(last_alpaca_ask_price)
    # print(last_oneInch_market_price)
    if (last_alpaca_ask_price > last_oneInch_market_price * (1 + min_arb_percent/100)):
        logger.info('Selling on ALPACA, Buying on 1Inch')
        if production:
            sell_order = post_Alpaca_order(
                trading_pair, 10, 'sell', 'market', 'gtc')
            logger.info('Selling on ALPACA Status: {0}'.format(
                sell_order['status']))
            buy_order_data = get_oneInch_swap_data(
                usdc_address, matic_address, last_oneInch_market_price*amount_to_exchange * (10**6))  # To buy 10 MATIC, we multiply its price by 10 (amount to exchnage) and then futher multiply it by 10^6 to get USDC value
            buy_order = signAndSendTransaction(buy_order_data)
    elif last_alpaca_ask_price < last_oneInch_market_price * (1 - min_arb_percent/100):
        logger.info('Buying on ALPACA, Selling on 1Inch')
        if production:
            buy_order = post_Alpaca_order(
                trading_pair, 10, 'buy', 'market', 'gtc')
            logger.info('Buying on ALPACA Status: {0}'.format(
                buy_order['status']))
            sell_order_data = get_oneInch_swap_data(
                matic_address, usdc_address, amount_to_exchange)
            sell_order = signAndSendTransaction(sell_order_data)
    else:
        # (abs(last_alpaca_ask_price - last_oneInch_market_price)/last_alpaca_ask_price < rebalance_percent/100):
        logger.info('No arbitrage opportunity available')
        logger.info('Rebalancing')
        rebalancing()
    pass

# Rebalance Portfolio


def rebalancing():
    current_matic_alpaca = get_positions()
    current_matic_1Inch = Web3.fromWei(
        w3.eth.getBalance(wallet_address), 'ether')
    if current_matic_alpaca > initial_matic_alpaca:
        logger.info('Rebalancing by Selling MATIC on ALPACA')
        if production:
            sell_order = post_Alpaca_order(
                trading_pair, current_matic_alpaca-initial_matic_alpaca, 'sell', 'market', 'gtc')
    elif current_matic_alpaca < initial_matic_alpaca:
        logger.info('Rebalancing by Buying MATIC on ALPACA')
        if production:
            buy_order = post_Alpaca_order(
                trading_pair, initial_matic_alpaca-current_matic_alpaca, 'buy', 'market', 'gtc')

    if current_matic_1Inch > initial_matic_1inch:
        logger.info('Rebalancing by Selling MATIC on 1Inch')
        if production:
            sell_order_data = get_oneInch_swap_data(
                matic_address, usdc_address, current_matic_1Inch-initial_matic_1inch)
            sell_order = signAndSendTransaction(sell_order_data)
    elif current_matic_1Inch < initial_matic_1inch:
        logger.info('Rebalancing by Buying MATIC on 1Inch')
        if production:
            buy_order_data = get_oneInch_swap_data(
                usdc_address, matic_address, last_oneInch_market_price * (initial_matic_1inch-current_matic_1Inch) * (10**6))
            buy_order = signAndSendTransaction(buy_order_data)
    pass


# establish web3 connection
w3 = connect_to_ETH_provider()

initial_matic_alpaca = get_positions()
initial_matic_1inch = Web3.fromWei(w3.eth.getBalance(wallet_address), 'ether')


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()
# run it!
# if __name__ == '__main__':
#     main()


#-----------------#
# Here are some examples of single methods/functions being executed
#-----------------#

# Get a trade quote directly from the blockchain
# response is a list like: [1533867641279495750, [0, 95, 5, 0, 0, 0, 0, 0, 0, 0]]
# where first item is amount, second is a list of how your order will be distributed across exchanges
# logger.info(one_inch_get_quote(ethereum, mcd_contract_address, amount_to_exchange))

#--- Making an Approval ---#
# check if MCD contract has allowance for provided account to spend tokens
# get_allowance(base_account)

# This will approve the one inch split contract to spend to spend amount_of_dai worth of base_account's tokens
# you will need to call this before trading your MCD/DAI on 1 inch. Will cost a small bit of ETH/gas
# approve_ERC20(amount_of_dai)

# check MCD again to confirm approval worked
# get_allowance(base_account)

#--- Using API to get data and make trades ---#
# get_api_quote_data("DAI", "ETH", amount_to_exchange)
# get_api_call_data("DAI", "ETH", amount_to_exchange)
