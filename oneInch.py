from subprocess import call
import config

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import logging
import json
import os
from web3 import Web3
# from abi import usdc_contract_abi
# import '../abi/usdc_contract.json'
# import 'abi/usdc_contract_abi.json'


# ENABLE LOGGING - options, DEBUG,INFO, WARNING?
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load up MCD and 1 Inch split contract ABIs
# one_inch_split_abi = json.load(open('abi/one_inch_split.json', 'r'))
# beta_one_inch_split_abi = json.load(open('abi/beta_one_inch_split.json', 'r'))
# mcd_abi = json.load(open('abi/mcd_join.json', 'r'))

production = False  # False to prevent any public TX from being sent
slippage = 1

# if MATIC --> USDC - (enter the amount in units Ether)
amount_to_exchange = Web3.toWei(1, 'ether')

# if USDC --> MATIC (using base unit, so 1 here = 1 DAI/MCD)
amount_of_usdc = 1000000


# one_inch_split_contract = Web3.toChecksumAddress(
#     '0xC586BeF4a0992C495Cf22e1aeEE4E446CECDee0E')  # 1 inch split contract

# beta_one_inch_split_contract = Web3.toChecksumAddress(
#     '0x50FDA034C0Ce7a8f7EFDAebDA7Aa7cA21CC1267e')  # Beta one split contract

matic_address = Web3.toChecksumAddress(
    '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE')  # ETHEREUM


usdc_address = Web3.toChecksumAddress(
    '0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174')  # USDC Token contract address

usdc_contract_abi = json.load(open('usdc_contract_abi.json', 'r'))
# print(usdc_contract_abi)

eth_provider_url = config.ALCHEMY_URL
base_account = Web3.toChecksumAddress(config.BASE_ACCOUNT)
wallet_address = base_account
private_key = config.PRIVATE_KEY
BASE_URL = 'https://api.1inch.io/v4.0/137'
# required - example: export ETH_PROVIDER_URL="https://mainnet.infura.io/v3/yourkeyhere77777"
# if 'ETH_PROVIDER_URL' in os.environ:
#     eth_provider_url = os.environ["ETH_PROVIDER_URL"]
# else:
#     logger.warning(
#         'No ETH_PROVIDER_URL has been set! Please set that and run the script again.')
#     quit()

# required - The Etheruem account that you will be making the trade/exchange from
# if 'BASE_ACCOUNT' in os.environ:
#     base_account = Web3.toChecksumAddress(os.environ["BASE_ACCOUNT"])
# else:
#     logger.warning(
#         'No BASE_ACCOUNT has been set! Please set that and run the script again.')
#     quit()


# private key for BASE_ACCOUNT
# if 'PRIVATE_KEY' in os.environ:
#     private_key = os.environ["PRIVATE_KEY"]
# else:
#     logger.warning(
#         'No private key has been set. Script will not be able to send transactions!')
#     private_key = False

# swapParams = {
#     fromTokenAddress: matic_address,  # matic address
#     toTokenAddress: usdc_address,  # usdc address
#     amount: amount_to_exchange,  # amount to exchange
#     fromAddress: wallet_address,  # wallet address
#     slippage: 1,
#     disableEstimate: false,
#     allowPartialFill: false,
# }


def main():
    '''
    These are examples of different functions in the script.
    Uncomment the command you want to run.
    '''
    # get price quote for 1 ETH in DAI right now
    # matic_price = one_inch_get_quote(
    #     ethereum, mcd_contract_address, Web3.toWei(1, 'ether'))
    usdc_token = w3.eth.contract(address=usdc_address, abi=usdc_contract_abi)
    usdc_balance = usdc_token.functions.balanceOf(wallet_address).call()
    print("USDC balance: {0}".format(usdc_balance))

    matic_price = get_api_quote_data(
        matic_address, usdc_address, amount_to_exchange)
    print("matic price is :", float(
        matic_price['toTokenAmount'])/10**6, "USDC")

    swap_data = get_api_swap_call_data(
        usdc_address, matic_address, amount_of_usdc)
    # print("swap data is :", swap_data)

    # allowance = get_allowance(usdc_address)
    # print("Allowance for USDC is: ", allowance['allowance'])

    # print("swap data is :", swap_data)
    # swap_txn = signAndSendTransaction(swap_data)  # swapping USDC for Matic
    # print("swap txn response is: ", Web3.toHex(swap_txn))

    # approval_txn = approve_ERC20(10)
    # approval_hash = signAndSendTransaction(approval_txn)
    # print("Approval hash is: ", w3.toHex(approval_hash))

    # allowance = get_allowance(usdc_address)
    # print("Allowance for USDC is: ", allowance['allowance'])

    # logger.info("1 ETH = {0} DAI on 1 Inch right now!".format(
    #     Web3.fromWei(matic_price['toTokenAmount'] / 10**6, 'ether')))

    # here is a ETH --> DAI exchange using 1 inch split contract (without api)
    # one_inch_token_swap(matic_address, usdc_address, amount_to_exchange)

    # Here are the steps for DAI --> ETH exchange using 1 inch split contract (without api)
    # We have to take an extra step to make this exchange by approving the 1 Inch contract
    # to spend some of our DAI first. You have to make sure the approve tx confirms before
    # you make the trade! So, just run this script twice, 1) to approve, wait for confirm
    # then 2) run the script again with just trade

    # 1) approve our DAI transfer (run once, first)
    # approve_ERC20(amount_of_dai)

    # wait for approve to confrim ^^

    # 2) then make trade/exchange
    # one_inch_token_swap(mcd_contract_address, ethereum, amount_of_dai)


def signAndSendTransaction(transaction_data):
    txn = w3.eth.account.signTransaction(transaction_data, private_key)
    tx_hash = w3.eth.sendRawTransaction(txn.rawTransaction)
    return tx_hash
    # const {rawTransaction} = await web3.eth.accounts.signTransaction(transaction, privateKey)

    # return await broadCastRawTransaction(rawTransaction)


def get_allowance(_token):
    '''
    Get allowance for a given token, the 1inch router is allowed to spend
    '''
    try:
        allowance = requests.get(
            '{0}/approve/allowance?tokenAddress={1}&walletAddress={2}'.format(BASE_URL, _token, wallet_address))
        logger.info('1inch allowance reply status code: {0}'.format(
            allowance.status_code))
        if allowance.status_code != 200:
            logger.info(
                "Undesirable response from 1 Inch! This is probably bad.")
            return False
        logger.info('get_allowance: {0}'.format(allowance.json()))

    except Exception as e:
        logger.exception(
            "There was an issue getting allowance for the token from 1 Inch: {0}".format(e))
        return False
    logger.info("allowance: {0}".format(allowance))
    return allowance.json()


def approve_ERC20(_amount_of_ERC):
    '''
    Send a transaction to MCD/DAI contract approving 1 Inch join contract to spend _amount_of_ERC worth of base_accounts tokens
    '''
    # load our contract
    # mcd_contract = web3.eth.contract(
    #     address=mcd_contract_address, abi=mcd_abi)

    allowance_before = get_allowance(wallet_address)
    logger.info("allowance before: {0}".format(allowance_before))

    try:
        approve_txn = requests.get(
            '{0}/approve/transaction?tokenAddress={1}&amount={2}'.format(BASE_URL, usdc_address, _amount_of_ERC))
        logger.info('1inch allowance reply status code: {0}'.format(
            approve_txn.status_code))
        if approve_txn.status_code != 200:
            logger.info(
                "Undesirable response from 1 Inch! This is probably bad.")
            return False
        logger.info('get_allowance: {0}'.format(approve_txn.json()))

    except Exception as e:
        logger.exception(
            "There was an issue allowing usdc spend from 1 Inch: {0}".format(e))
        return False

    approve_txn = approve_txn.json()
    # logger.info("allowance: {0}".format(allowance))

    # get our nonce
    nonce = w3.eth.getTransactionCount(wallet_address)

    # encode our data
    # data = mcd_contract.encodeABI(fn_name="approve", args=[
    #     one_inch_split_contract, _amount_of_ERC])
    print("gas price is:", w3.fromWei(int(approve_txn['gasPrice']), 'gwei'))

    tx = {
        'nonce': nonce,
        'to': usdc_address,
        'chainId': 137,
        # 'value': approve_txn['value'],
        'gasPrice': w3.toWei(70, 'gwei'),
        'from': wallet_address,
        'data': approve_txn['data']
    }

    # get gas estimate
    # gas_estimate = w3.eth.estimateGas(tx)
    tx['gas'] = 80000
    # print("gas estimate: {0}".format(gas_estimate))
    # tx["gas"] = approve_txn['gasPrice']

    logger.info('transaction data: {0}'.format(tx))

    return tx

    # # sign and broadcast our trade
    # if private_key and production == True:
    #     try:
    #         signed_tx = web3.eth.account.signTransaction(tx, private_key)
    #     except:
    #         logger.exception("Failed to created signed TX!")
    #         return False
    #     try:
    #         tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)
    #         logger.info("TXID from 1 Inch: {0}".format(web3.toHex(tx_hash)))
    #     except:
    #         logger.warning("Failed sending TX to 1 inch!")
    #         return False
    # else:
    #     logger.info('No private key found! Transaction has not been broadcast!')


def get_api_swap_call_data(_from_coin, _to_coin, _amount_to_exchange):
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


def get_api_quote_data(_from_coin, _to_coin, _amount_to_exchange):
    '''
    Get trade quote data from 1Inch API
    '''
    try:
        quote = requests.get(
            '{0}/quote?fromTokenAddress={1}&toTokenAddress={2}&amount={3}'.format(BASE_URL, _from_coin, _to_coin, _amount_to_exchange))
        logger.info('1inch quote reply status code: {0}'.format(
            quote.status_code))
        if quote.status_code != 200:
            logger.info(
                "Undesirable response from 1 Inch! This is probably bad.")
            return False
        logger.info('get_api_quote_data: {0}'.format(quote.json()))

    except Exception as e:
        logger.exception(
            "There was an issue getting trade quote from 1 Inch: {0}".format(e))
        return False

    return quote.json()


def one_inch_token_swap(_from_token, _to_token, _amount):
    '''
    Used to swap tokens on 1Inch directly through the one inch split contract
    '''
    # get quote for trade,
    # quote = one_inch_get_quote(_from_token, _to_token, _amount)
    quote = get_api_quote_data(_from_token, _to_token, _amount)

    # min coins to accept, taken from our quote
    min_return = quote['toTokenAmount']/(10**6)

    # list of dist across exchanges like: [99, 0, 1, 0, 0, 0, 0, 0, 0, 0]
    # distribution = quote[1]

    # use all available exchanges
    disable_flags = 0

    # load our contract
    one_inch_join = web3.eth.contract(
        address=one_inch_split_contract, abi=one_inch_split_abi)

    # get our nonce
    nonce = web3.eth.getTransactionCount(wallet_address)

    # craft transaction call data
    data = one_inch_join.encodeABI(fn_name="swap", args=[
        _from_token, _to_token, _amount, min_return, distribution, disable_flags])

    # if ETH --> DAI then value is exchange _amount, if DAI-->ETH then value != _amount
    if _from_token == mcd_contract_address:
        value = 0
    else:
        value = _amount

    tx = {
        'nonce': nonce,
        'to': one_inch_split_contract,
        'value': value,
        'gasPrice': web3.eth.gasPrice,
        'from': wallet_address,
        'data': data
    }

    # get gas estimate
    gas = web3.eth.estimateGas(tx)
    tx["gas"] = gas

    logger.info('transaction data: {0}'.format(tx))

    # sign and broadcast our trade
    if private_key and production == True:
        try:
            signed_tx = web3.eth.account.signTransaction(tx, private_key)
        except:
            logger.exception("Failed to created signed TX!")
            return False
        try:
            tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)
            logger.info("TXID: {0}".format(web3.toHex(tx_hash)))
        except:
            logger.warning("Failed sending TX to 1 inch!")
            return False
    else:
        logger.info('No private key found! Transaction has not been broadcast!')


def one_inch_get_quote(_from_token, _to_token, _amount):
    '''
    Get quote data from one inch join contract using on-chain call
    '''
    # load our contract
    one_inch_join = web3.eth.contract(
        address=config.polygon_oracle, abi=config.oracli_abi)

    # # load beta contract
    # beta_one_inch_join = web3.eth.contract(
    #     address=beta_one_inch_split_contract, abi=beta_one_inch_split_abi)

    # make call request to contract on the Ethereum blockchain
    contract_response = one_inch_join.functions.getExpectedReturn(
        _from_token, _to_token, _amount, 100, 0).call({'from': wallet_address})

    '''
    work in progress. I'm not sure that it's safe to get quotes onchain yet though
    https://github.com/CryptoManiacsZone/1inchProtocol
    The sequence of number of pieces source volume could be splitted (Works like granularity, 
    higly affects gas usage. Should be called offchain, but could be called onchain if user swaps not his own funds, 
    but this is still considered as not safe)
    '''
    parts = 10  # still not 100% what parts means here. I _think_ maybe it maps to total number of exchanges to use
    # static for now, might be better if it was dynamic
    gas_price = web3.toWei('100', 'gwei')

    beta_contract_response = beta_one_inch_join.functions.getExpectedReturnWithGas(
        _from_token, _to_token, _amount, parts, 0, gas_price *
        contract_response[0]
    ).call({'from': wallet_address})

    logger.info("contract response: {0}".format(contract_response))
    logger.info("beta contract response: {0}".format(beta_contract_response))
    return contract_response


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

# run it!
if __name__ == '__main__':
    main()


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
