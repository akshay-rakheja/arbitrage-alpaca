#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

# OneInch API
BASE_URL = 'https://api.1inch.io/v4.0/137'
# if MATIC --> USDC - (enter the amount in units Ether)
amount_to_exchange = Web3.toWei(1, 'ether')

# if USDC --> MATIC (using base unit, so 1 here = 1 DAI/MCD)
amount_of_usdc = Web3.toWei(1, 'ether')

matic_address = Web3.toChecksumAddress(
    '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE')  # ETHEREUM


usdc_address = Web3.toChecksumAddress(
    '0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174')  # USDC Token contract address

eth_provider_url = config.ALCHEMY_URL
base_account = Web3.toChecksumAddress(config.BASE_ACCOUNT)
wallet_address = base_account
private_key = config.PRIVATE_KEY


# Alpaca API
alpaca = REST(config.APCA_API_KEY_ID, config.APCA_API_SECRET_KEY,
              'https://paper-api.alpaca.markets')

HEADERS = {'APCA-API-KEY-ID': config.APCA_API_KEY_ID,
           'APCA-API-SECRET-KEY': config.APCA_API_SECRET_KEY}


trading_pair = 'MATICUSD'  # Checking quotes and trading MATIC against USD
exchange = 'FTXU'  # FTXUS
DATA_URL = 'https://data.alpaca.markets'

last_alpaca_ask_price = 0
last_oneInch_market_price = 0

trade_size = 10


async def main():
    '''
    These are examples of different functions in the script.
    Uncomment the command you want to run.
    '''
    # get price quote for 1 ETH in DAI right now
    # matic_price = one_inch_get_quote(
    #     ethereum, mcd_contract_address, Web3.toWei(1, 'ether'))
    while True:
        l1 = loop.create_task(get_oneInch_quote_data(
            matic_address, usdc_address, amount_to_exchange))
        l2 = loop.create_task(get_Alpaca_quote_data(trading_pair, exchange))
        # Wait for the tasks to finish
        await asyncio.wait([l1, l2])
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
        last_oneInch_market_price = int(quote.json()['toTokenAmount'])/10**6
        logger.info('OneInch Price: {0}'.format(last_oneInch_market_price))
    except Exception as e:
        logger.exception(
            "There was an issue getting trade quote from 1 Inch: {0}".format(e))
        return False

    return quote.json()


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
        last_alpaca_ask_price = quote.json()['quote']['ap']
        logger.info('Alpaca Price: {0}'.format(last_alpaca_ask_price))
    except Exception as e:
        logger.exception(
            "There was an issue getting trade quote from Alpaca: {0}".format(e))
        return False

    return quote.json()


async def get_oneInch_swap_data(_from_coin, _to_coin, _amount_to_exchange):
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

        logger.info('get_api_call_data: {0}'.format(call_data))

    except Exception as e:
        logger.warning(
            "There was a issue getting get contract call data from 1 inch: {0}".format(e))
        return False

    return tx


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
    txn = w3.eth.account.signTransaction(transaction_data, private_key)
    tx_hash = w3.eth.sendRawTransaction(txn.rawTransaction)
    return tx_hash


# establish web3 connection
w3 = connect_to_ETH_provider()


async def check_arbitrage():
    pass


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
