import pyupbit
import config

upbit = 0
hold_position = 0
ask_price = 0
bid_price = 0

ask_price_pre = 0
bid_price_pre = 0

krw = 0

orders = []
order_details = {}

def initialize() :
    global upbit
    api_key = config.get_config('UB_API_KEY')
    secret_key = config.get_config('UB_SECRET_KEY')
    upbit = pyupbit.Upbit(api_key, secret_key)
    return 0

def update_balance() :
    global hold_position
    hold_position = upbit.get_balance('USDT')
    return 0

def update_balance_krw() :
    global krw
    krw = round(upbit.get_balance('KRW'))
    return 0

def update_orderbook() :
    global ask_price
    global bid_price
    order_book = pyupbit.get_orderbook('KRW-USDT')
    ask_price = order_book['orderbook_units'][0]['ask_price']
    bid_price = order_book['orderbook_units'][0]['bid_price']
    return 0

def update_orderbook_pre() :
    global ask_price_pre
    global bid_price_pre
    order_book = pyupbit.get_orderbook('KRW-USDT')
    ask_price_pre = order_book['orderbook_units'][0]['ask_price']
    bid_price_pre = order_book['orderbook_units'][0]['bid_price']
    return 0

def buy_market_order(symbol, amount) :
    upbit.buy_limit_order('KRW-'+symbol, round(ask_price*1.1), amount)
    return 0

def sell_market_order(symbol, amount) :
    upbit.sell_limit_order('KRW-'+symbol, bid_price, amount)
    return 0

def buy_limit_order(symbol, price, amount) :
    global orders
    order = upbit.buy_limit_order('KRW-'+symbol, price, amount)
    if len(orders) == 0 :
        orders.append(order)
    else :
        orders[0] = order
    return 0

def sell_limit_order(symbol, price, amount) :
    global orders
    order = upbit.sell_limit_order('KRW-'+symbol, price, amount)
    if len(orders) == 0 :
        orders.append(order)
    else :
        orders[0] = order
    return 0

def update_orders() :
    global order_details
    order_details = {}
    for order in orders :
        order_detail = upbit.get_order(order['uuid'])
        order_details[order['uuid']] = order_detail
        #try :
        #    order_details[order['uuid']] = order_detail
        #    if order_detail['state'] != 'wait' :
        #        orders.remove(order)
        #except :
        #    upbit.cancel_order(order['uuid'])
        #    orders.remove(order)
    return 0


    for order in orders:
        order_completed = upbit.get_order(order['uuid'])

        total_krw = 0
        total_vol = 0
        for trade in order_completed['trades'] :
            price  = float(trade['price'])
            volume = float(trade['volume'])
            total_krw += (price*volume)
            total_vol += volume
        order_price_BUY = round(total_krw/total_vol, 2)
    return 0

def capture_orderbook() :
    global ask_price
    global bid_price
    ask_price = ask_price_pre
    bid_price = bid_price_pre
    return 0

