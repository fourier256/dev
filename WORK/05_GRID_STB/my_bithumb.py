
import time
from datetime import datetime, timedelta
import requests
import json
import datetime
from datetime import datetime, timedelta

import pybithumb
import config
from my_util import print_log

bithumb = 0

max_position = 10000000
hold_position = 0

market_price = 0
ask_price = 0
bid_price = 0

orders = []
order_details = {}

candle = []
ma_arr = []

def initialize() :
    global bithumb
    api_key = config.get_config('BT_API_KEY')
    secret_key = config.get_config('BT_SECRET_KEY')
    bithumb = pybithumb.Bithumb(api_key, secret_key)
    return 0

def init_candle(n_day=1) :
    global market_price
    global candle
    symbol = 'USDT'
    count = 60
    now = datetime.now()
    print('total_hh = ' + str(24*n_day))
    for iHH in range(24*n_day) :
        if iHH%24 == 0 :
            print(iHH/24)
        past_time = now - timedelta(hours=iHH)
        formatted_time = past_time.strftime("%y-%m-%dT%H:%M")
        url = "https://api.bithumb.com/v1/candles/minutes/1?market=KRW-USDT&count=60&to=20"+formatted_time
        headers = {"accept": "application/json"}
        response = requests.get(url, headers=headers)
        data = json.loads(response.text)
        #print(data[0]['candle_date_time_kst'] + ' : ' + data[0]['trade_price'])
        for iMM in range(60) :
            market_price = float(data[iMM]['trade_price'])
            candle.append(get_kp())
        #time.sleep(0.1)
    candle = list(reversed(candle))
    update_market_price()
    update_candle(get_kp())
    return 0

def init_ma_arr() :
    for iMM in range(len(candle)-1440) :
        ma_arr.append(sum(candle[iMM:1440+iMM])/1440)
    return 0

def update_candle(kp) :
    candle.pop(0)
    #candle.insert(0, kp)
    candle.append(kp)
    return 0

def update_ma(ma) :
    ma_arr.pop(0)
    ma_arr.append(ma)
    return 0

def update_ma_arr(ma) :
    update_ma(ma)
    return 0

def update_balance() :
    global hold_position
    balance = bithumb.get_balance('USDT')
    while balance==None :
        print('get_balance retry')
        balance = bithumb.get_balance('USDT')
    hold_position = balance[0]
    return 0

def update_market_price() :
    global market_price
    market_price_pre = pybithumb.get_current_price('USDT')
    if market_price_pre != 0 and market_price_pre != None:
        market_price = market_price_pre
    return 0

def update_orderbook() :
    global ask_price
    global bid_price
    order_book = pybithumb.get_orderbook('USDT')
    while order_book == None :
        order_book = pybithumb.get_orderbook('USDT')
        print('pybithumb get_orderbook error, retry')
    ask_price = order_book['asks'][0]['price']
    bid_price = order_book['bids'][0]['price']
    return 0

def buy_limit_order(symbol, price, amount):
    order = bithumb.buy_limit_order(symbol, price, amount)
    orders.append(order)
    #print_log('order = ' + str(order))
    return 0

def buy_market_order(symbol, amount):
    bithumb.buy_limit_order(symbol, ask_price, amount)
    return 0

def sell_limit_order(symbol, price, amount):
    order = bithumb.sell_limit_order(symbol, price, amount)
    orders.append(order)
    #print_log('order = ' + str(order))
    return 0

def sell_market_order(symbol, amount):
    bithumb.sell_limit_order(symbol, bid_price, amount)
    return 0

def update_orders() :
    global order_details
    order_details = {}
    for order in orders :
        order_detail = bithumb.get_order_completed(order)
        try :
            order_details[order[2]] = order_detail
            if order_detail['data']['order_status'] != 'Pending' :
                orders.remove(order)
        except :
            bithumb.cancel_order(order)
            orders.remove(order)
    return 0

def cancel_order(order_id) :
    for order in orders :
        if order[2] == order_id :
            bithumb.cancel_order(order)
            return 0
    return 1

def get_kp() :
    #exchange = 1000
    #bn_price = 1
    #bn_krw = bn_price * exchange
    #kp = round((market_price - bn_krw)/bn_krw, 6)
    kp = market_price
    return kp
