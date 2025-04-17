import pyupbit
import config

upbit = 0
hold_position = 0
ask_price = 0
bid_price = 0
krw = 0

order_BUY = 0
order_price_BUY = 0

order_SELL = 0
order_price_SELL = 0

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

def buy_market_order(symbol, amount) :
    global order_BUY
    print('ub buy_market_order ' + str(amount))
    #order_BUY = upbit.buy_market_order('KRW-'+symbol, amount)
    order_BUY = upbit.buy_limit_order('KRW-'+symbol, round(ask_price*1.1), amount)
    return 0

def sell_market_order(symbol, amount) :
    global order_SELL
    print('ub sell_market_order' + str(amount))
    #order_SELL = upbit.sell_market_order('KRW-'+symbol, amount)
    order_SELL = upbit.sell_limit_order('KRW-'+symbol, bid_price, amount)
    return 0

def update_order_BUY() :
    global order_price_BUY
    print(order_BUY)
    order_completed = upbit.get_order(order_BUY['uuid'])
    total_krw = 0
    total_vol = 0
    for trade in order_completed['trades'] :
        price  = float(trade['price'])
        volume = float(trade['volume'])
        total_krw += (price*volume)
        total_vol += volume
    order_price_BUY = round(total_krw/total_vol, 2)
    return 0

def update_order_SELL() :
    global order_price_SELL
    #order_completed = upbit.get_order(order_SELL['uuid'])
    #total_krw = 0
    #total_vol = 0
    #for trade in order_completed['trades'] :
        #price  = float(trade['price'])
        #volume = float(trade['volume'])
        #total_krw += (price*volume)
        #total_vol += volume
    #order_price_SELL = round(total_krw/total_vol, 2)
    order_price_SELL = bid_price
    return 0
