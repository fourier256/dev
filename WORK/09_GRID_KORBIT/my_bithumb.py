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
    api_key = config.get_config('BT_API_KEY')
    secret_key = config.get_config('BT_SECRET_KEY')
    korbit = pykorbit.Korbit(api_key, secret_key)
    return 0

def init_candle(n_day=1):
    global market_price
    global candle
    symbol = 'USDT'
    count = 60
    now = datetime.now() + timedelta(hours=9)
    print('total_hh = ' + str(24*n_day))
    
    for iHH in range(24 * n_day):
        if iHH % 24 == 0:
            print(iHH / 24)
        past_time = now - timedelta(hours=iHH)
        formatted_time = past_time.strftime("%y-%m-%dT%H:%M")
        url = f"https://api.korbit.co.kr/v1/candles/1m?currency_pair=krw_{symbol}&count=60&to={formatted_time}"
        response = requests.get(url)
        data = response.json()
        
        for iMM in range(60):
            market_price = float(data[iMM]['trade_price'])
            candle.append(get_kp())
    
    candle = list(reversed(candle))
    update_market_price()
    update_candle(get_kp())
    return 0

def init_ma_arr():
    for iMM in range(len(candle)-1440):
        ma_arr.append(round(sum(candle[iMM:1440+iMM])/1440, 3))
    return 0

def update_candle(kp):
    candle.pop(0)
    candle.append(kp)
    return 0

def update_ma(ma):
    ma_arr.pop(0)
    ma_arr.append(ma)
    return 0

def update_balance():
    global hold_position
    global krw
    balance = korbit.get_balance()
    hold_position = balance['USDT']
    krw = balance['KRW']
    return 0

def update_market_price():
    global market_price
    market_price_pre = korbit.get_orderbook('krw_usdt')['last_price']
    if market_price_pre:
        market_price = market_price_pre
    return 0

def update_orderbook():
    global ask_price
    global bid_price
    order_book = korbit.get_orderbook('krw_usdt')
    
    if order_book:
        ask_price = float(order_book['asks'][0]['price'])
        bid_price = float(order_book['bids'][0]['price'])
    return 0

def buy_limit_order(symbol, price, amount):
    order = korbit.buy_limit_order(symbol, price, amount)
    orders.append(order)
    return 0

def buy_market_order(symbol, amount):
    korbit.buy_market_order(symbol, amount)
    return 0

def sell_limit_order(symbol, price, amount):
    order = korbit.sell_limit_order(symbol, price, amount)
    orders.append(order)
    return 0

def sell_market_order(symbol, amount):
    korbit.sell_market_order(symbol, amount)
    return 0

def update_orders():
    global order_details
    order_details = {}
    for order in orders:
        order_detail = korbit.get_order_detail(order)
        try:
            order_details[order['id']] = order_detail
            if order_detail['status'] != 'Pending':
                orders.remove(order)
        except:
            korbit.cancel_order(order['id'])
            orders.remove(order)
    return 0

def cancel_order(order_id):
    for order in orders:
        if order['id'] == order_id:
            korbit.cancel_order(order['id'])
            return 0
    return 1

def get_kp():
    kp = market_price
    return kp

def withdraw_coin(symbol, amount, address, net_type, destination=None):
    withdrawal_data = {
        'currency': symbol,
        'amount': amount,
        'address': address,
        'net_type': net_type
    }
    result = korbit.withdraw_coin(withdrawal_data)
    return result
