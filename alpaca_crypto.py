from turtle import pos
from webbrowser import get
from wsgiref.headers import Headers
from alpaca_trade_api.rest import REST, TimeFrame
import config
import requests
import logging
from multiprocessing import Process
import time

# ENABLE LOGGING - options, DEBUG,INFO, WARNING?
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# alpaca = REST(config.APCA_API_KEY_ID, config.APCA_API_SECRET_KEY,
#               'https://paper-api.alpaca.markets')

HEADERS = {'APCA-API-KEY-ID': config.APCA_API_KEY_ID,
           'APCA-API-SECRET-KEY': config.APCA_API_SECRET_KEY}

BASE_URL = 'https://paper-api.alpaca.markets'
trading_pair = 'MATICUSD'  # Checking quotes and trading MATIC against USD
exchange = 'FTXU'  # FTXUS
DATA_URL = 'https://data.alpaca.markets'


def get_api_quote_data(trading_pair, exchange):
    '''
    Get trade quote data from 1Inch API
    '''
    try:
        quote = requests.get(
            '{0}/v1beta1/crypto/{1}/quotes/latest?exchange={2}'.format(DATA_URL, trading_pair, exchange), headers=HEADERS)
        logger.info('Alpaca quote reply status code: {0}'.format(
            quote.status_code))
        if quote.status_code != 200:
            logger.info(
                "Undesirable response from Alpaca! {}".format(quote.json()))
            return False
        logger.info('get_api_quote_data: {0}'.format(quote.json()))

    except Exception as e:
        logger.exception(
            "There was an issue getting trade quote from Alpaca: {0}".format(e))
        return False

    return quote.json()


def get_account_details():
    '''
    Get Alpaca Trading Account Details
    '''
    try:
        account = requests.get(
            '{0}/v2/account'.format(BASE_URL), headers=HEADERS)
        logger.info('Alpaca account reply status code: {0}'.format(
            account.status_code))
        if account.status_code != 200:
            logger.info(
                "Undesirable response from Alpaca! {}".format(account.json()))
            return False
        logger.info('get_account_details: {0}'.format(account.json()))
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
            '{0}/v2/positions'.format(BASE_URL), headers=HEADERS)
        logger.info('Alpaca positions reply status code: {0}'.format(
            positions.status_code))
        if positions.status_code != 200:
            logger.info(
                "Undesirable response from Alpaca! {}".format(positions.json()))
            return False
        # positions = positions[0]
        matic_position = positions.json()[0]['qty']
        logger.info('Matic Position on Alpaca: {0}'.format(matic_position))
    except Exception as e:
        logger.exception(
            "There was an issue getting positions from Alpaca: {0}".format(e))
        return False
    return matic_position


def post_order(symbol, qty, side, type, time_in_force):
    '''
    Post an order to Alpaca
    '''
    try:
        order = requests.post(
            '{0}/v2/orders'.format(BASE_URL), headers=HEADERS, json={
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
        logger.info('post_order: {0}'.format(order.json()))
    except Exception as e:
        logger.exception(
            "There was an issue posting order to Alpaca: {0}".format(e))
        return False
    return order.json()


def main():
    '''
    These are examples of different functions in the script.
    Uncomment the command you want to run.
    '''
    # get price quote for 1 ETH in DAI right now
    # matic_price = one_inch_get_quote(
    #     ethereum, mcd_contract_address, Web3.toWei(1, 'ether'))
    # while True:
    matic_price = get_api_quote_data(trading_pair, exchange)
    print("matic price is :", matic_price['quote']['ap'])
    # print("Account details are: ", get_account_details())
    print("Cash balance is: ", get_account_details()['cash'])
    # print("Open orders are: ", get_open_orders())
    if(get_open_orders()):
        print("Open orders are: ", get_open_orders())
    else:
        print("No open orders")

    get_positions()
    # buying_matic = post_order(trading_pair, 10, 'buy', 'market', 'gtc')
    # print("Buying matic order response: ", buying_matic)

    # selling_matic = post_order(trading_pair, 20, 'buy', 'market', 'gtc')
    # print("Selling matic order response: ", selling_matic)
    # time.sleep(2)


# in_position_quantity = 0
# pending_orders = {}
# dollar_amount = 1000
# logfile = 'trade.log'


# def check_order_status():
#     global in_position_quantity

#     removed_order_ids = []

#     print("{} - checking order status".format(datetime.now().isoformat()))

#     if len(pending_orders.keys()) > 0:
#         print("found pending orders")
#         for order_id in pending_orders:
#             order = alpaca.get_order(order_id)

#             if order.filled_at is not None:
#                 filled_message = "order to {} {} {} was filled {} at price {}\n".format(
#                     order.side, order.qty, order.symbol, order.filled_at, order.filled_avg_price)
#                 print(filled_message)
#                 with open(logfile, 'a') as f:
#                     f.write(str(order))
#                     f.write(filled_message)

#                 if order.side == 'buy':
#                     in_position_quantity = float(order.qty)
#                 else:
#                     in_position_quantity = 0

#                 removed_order_ids.append(order_id)
#             else:
#                 print("order has not been filled yet")

#     for order_id in removed_order_ids:
#         del pending_orders[order_id]


# def send_order(symbol, quantity, side):
#     print("{} - sending {} order".format(datetime.now().isoformat(), side))
#     order = alpaca.submit_order(symbol, quantity, side, 'market')
#     print(order)
#     pending_orders[order.id] = order


# def get_bars():
#     print("{} - getting bars".format(datetime.now().isoformat()))
#     data = vbt.CCXTData.download(
#         ['SOLUSDT'], start='30 minutes ago', timeframe='1m')
#     df = data.get()
#     df.ta.stoch(append=True)
#     print(df)

#     last_k = df['STOCHk_14_3_3'].iloc[-1]
#     last_d = df['STOCHd_14_3_3'].iloc[-1]
#     last_close = df['Close'].iloc[-1]

#     print(last_k)
#     print(last_d)
#     print(last_close)

#     if last_d < 40 and last_k > last_d:
#         # min order size for SOL is 0.01
#         if in_position_quantity == 0 and (dollar_amount / last_close) >= 0.1:
#             # buy
#             print("------ Trying to buy -----: ", dollar_amount / last_close)
#             send_order('ETHUSD', round(dollar_amount / last_close, 3), 'buy')
#         else:
#             print("== already in position, nothing to do ==")

#     if last_d > 80 and last_k < last_d:
#         if in_position_quantity > 0:
#             # sell
#             send_order('ETHUSD', in_position_quantity, 'sell')
#         else:
#             print("== you have nothing to sell ==")


# manager = vbt.ScheduleManager()
# manager.every().do(check_order_status)
# manager.every().minute.at(':00').do(get_bars)
# manager.start()


# from alpaca_trade_api.stream import Stream
# import config
# import os


# async def print_trade(t):
#     print('trade', t)


# async def print_quote(q):
#     print('quote', q)


# async def print_trade_update(tu):
#     print('trade update', tu)


# async def print_crypto_trade(t):
#     print('crypto trade', t)


# def main():

#     BASE_URL = "https://paper-api.alpaca.markets"
#     CRYPTO_URL = 'https://data.alpaca.markets/v1beta1/crypto'
#     ALPACA_API_KEY = config.APCA_API_KEY_ID
#     ALPACA_SECRET_KEY = config.APCA_API_SECRET_KEY

#     feed = 'iex'  # <- replace to SIP if you have PRO subscription
#     stream = Stream(key_id=ALPACA_API_KEY,
#                     secret_key=ALPACA_SECRET_KEY, base_url=BASE_URL, raw_data=True, data_stream_url=CRYPTO_URL)
#     # stream.subscribe_trade_updates(print_trade_update)
#     stream.subscribe_trades(print_trade, 'BTCUSD')
#     # stream.subscribe_quotes(print_quote, 'IBM')
#     # stream.subscribe_crypto_trades(print_crypto_trade, 'BTCUSD')
#     # print(stream)

#     @stream.on_bar('MSFT')
#     async def _(bar):
#         print('bar', bar)

#     # @stream.on_updated_bar('MSFT')
#     # async def _(bar):
#     #     print('updated bar', bar)

#     @stream.on_status("*")
#     async def _(status):
#         print('status', status)

#     # @stream.on_luld('AAPL', 'MSFT')
#     # async def _(luld):
#     #     print('LULD', luld)

#     stream.run()
if __name__ == "__main__":
    main()
