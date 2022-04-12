# from alpaca_trade_api.rest import REST, TimeFrame

# alpaca = REST(config.APCA_API_KEY_ID, config.APCA_API_SECRET_KEY,
#               'https://paper-api.alpaca.markets')

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


from alpaca_trade_api.stream import Stream
import config
import os


async def print_trade(t):
    print('trade', t)


async def print_quote(q):
    print('quote', q)


async def print_trade_update(tu):
    print('trade update', tu)


async def print_crypto_trade(t):
    print('crypto trade', t)


def main():

    BASE_URL = "https://paper-api.alpaca.markets"
    CRYPTO_URL = 'https://data.alpaca.markets/v1beta1/crypto'
    ALPACA_API_KEY = config.APCA_API_KEY_ID
    ALPACA_SECRET_KEY = config.APCA_API_SECRET_KEY

    feed = 'iex'  # <- replace to SIP if you have PRO subscription
    stream = Stream(key_id=ALPACA_API_KEY,
                    secret_key=ALPACA_SECRET_KEY, base_url=BASE_URL, raw_data=True, data_stream_url=CRYPTO_URL)
    # stream.subscribe_trade_updates(print_trade_update)
    stream.subscribe_trades(print_trade, 'BTCUSD')
    # stream.subscribe_quotes(print_quote, 'IBM')
    # stream.subscribe_crypto_trades(print_crypto_trade, 'BTCUSD')
    # print(stream)

    @stream.on_bar('MSFT')
    async def _(bar):
        print('bar', bar)

    # @stream.on_updated_bar('MSFT')
    # async def _(bar):
    #     print('updated bar', bar)

    @stream.on_status("*")
    async def _(status):
        print('status', status)

    # @stream.on_luld('AAPL', 'MSFT')
    # async def _(luld):
    #     print('LULD', luld)

    stream.run()


if __name__ == "__main__":
    main()
