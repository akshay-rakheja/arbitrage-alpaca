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


# Alpaca API
alpaca = REST(config.APCA_API_KEY_ID, config.APCA_API_SECRET_KEY,
              'https://paper-api.alpaca.markets')

HEADERS = {'APCA-API-KEY-ID': config.APCA_API_KEY_ID,
           'APCA-API-SECRET-KEY': config.APCA_API_SECRET_KEY}


trading_pair = 'MATICUSD'  # Checking quotes and trading MATIC against USD
exchange = 'FTXU'  # FTXUS
DATA_URL = 'https://data.alpaca.markets'


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
        await asyncio.wait([l1, l2])
        await asyncio.sleep(5)
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
        logger.info('OneInch Price: {0}'.format(
            int(quote.json()['toTokenAmount'])/10**6))
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
        logger.info('Alpaca Price: {0}'.format(quote.json()['quote']['ap']))
    except Exception as e:
        logger.exception(
            "There was an issue getting trade quote from Alpaca: {0}".format(e))
        return False

    return quote.json()

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
