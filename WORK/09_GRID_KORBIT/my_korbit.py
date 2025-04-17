import time
from datetime import datetime, timedelta
import requests
import json
import pykorbit
import config
from my_util import print_log

korbit = None

max_position = 10000000
hold_position = 0
krw = 0

market_price = 0
ask_price = 0
bid_price = 0

orders = []
order_details = {}

candle = []
ma_arr = []

def initialize():
    global korbit
    api_key = config.get_config('KB_API_KEY')
    secret_key = config.get_config('KB_SECRET_KEY')
    korbit = pykorbit.Korbit(api_key, secret_key)
    return 0

def init_candle(n_day=1):
    global market_price
    global candle
    symbol = 'usdt_krw'
    count = 60
    now = datetime.now() + timedelta(hours=9)

    for iHH in range(24 * n_day):
        if iHH % 24 == 0:
            print(iHH // 24)
        past_time = now - timedelta(hours=iHH)
        formatted_time = past_time.strftime("%Y-%m-%dT%H:%M")
        url = f"https://api.korbit.co.kr/v1/candles/minute?currency_pair={symbol}&time={formatted_time}&interval=1&count={count}"
        headers = {"accept": "application/json"}
        response = requests.get(url, headers=headers)
        data = json.loads(response.text)

        for iMM in range(len(data)):
            market_price = float(data[iMM]['close'])
            candle.append(market_price)

    candle = list(reversed(candle))
    update_market_price()
    update_candle(market_price)
    return 0

def init_ma_arr():
    for iMM in range(len(candle) - 1440):
        ma_arr.append(round(sum(candle[iMM:1440 + iMM]) / 1440, 3))
    return 0

def update_candle(price):
    candle.pop(0)
    candle.append(price)
    return 0

def update_ma(ma):
    ma_arr.pop(0)
    ma_arr.append(ma)
    return 0

def update_balance():
    global hold_position
    global krw
    balance = korbit.get_balances()
    while balance is None:
        print('get_balance retry')
        balance = korbit.get_balances()
    
    hold_position = float(balance.get('usdt', {}).get('available', 0))
    krw = float(balance.get('krw', {}).get('available', 0))
    return 0

def update_market_price():
    global market_price
    market_price_pre = korbit.get_ticker('usdt_krw')['last']
    if market_price_pre:
        market_price = float(market_price_pre)
    return 0

def update_orderbook():
    global ask_price, bid_price
    order_book = korbit.get_orderbook('usdt_krw')
    while order_book is None:
        order_book = korbit.get_orderbook('usdt_krw')
        print('korbit get_orderbook error, retry')

    ask_price = float(order_book['asks'][0][0])
    bid_price = float(order_book['bids'][0][0])
    return 0

def buy_limit_order(price, amount):
    order = korbit.buy('usdt_krw', price, amount, 'limit')
    orders.append(order)
    return order

def buy_market_order(amount):
    order = korbit.buy('usdt_krw', amount, order_type='market')
    return order

def sell_limit_order(price, amount):
    order = korbit.sell('usdt_krw', price, amount, 'limit')
    orders.append(order)
    return order

def sell_market_order(amount):
    order = korbit.sell('usdt_krw', amount, order_type='market')
    return order

def update_orders():
    global order_details
    order_details = {}
    for order in orders:
        order_detail = korbit.get_order_status(order['order_id'])
        try:
            order_details[order['order_id']] = order_detail
            if order_detail['status'] != 'open':
                orders.remove(order)
        except:
            korbit.cancel_order(order['order_id'])
            orders.remove(order)
    return 0

def cancel_order(order_id):
    for order in orders:
        if order['order_id'] == order_id:
            korbit.cancel_order(order_id)
            return 0
    return 1

def withdraw_coin(symbol, amount, address, net_type):
    result = korbit.withdraw(symbol, amount, address, net_type)
    return result