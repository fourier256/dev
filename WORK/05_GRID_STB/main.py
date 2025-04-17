import time
import my_upbit as ub
import my_bithumb as bt
import my_telegram_bot
from my_util import print_log
from my_util import get_buf
from numpy import std

AMOUNT   = 4500
KP       = 0
RANGE    = 0
MIN_HOLD = 0
MAX_HOLD = 0
HOLD     = 0
COMPLETE = 0

RANGE_OLD = 0

def initialize() :
    global COMPLETE
    ub.initialize()
    bt.initialize()
    bt.init_candle(2)
    bt.init_ma_arr()
    COMPLETE = bt.market_price
    RANGE = get_RANGE(bt.get_kp(), get_CENTER(), get_STD())
    bt.update_balance()
    bt.update_orderbook()
    print_log('Start GRID_STB')
    print_log('HOLD = ' + str(bt.hold_position))
    if bt.hold_position <= AMOUNT*(20-1) :
        print_log('BID order at ' + str(bt.bid_price))
        bt.buy_limit_order('USDT', bt.bid_price, AMOUNT)
    if bt.hold_position >= AMOUNT :
        print_log('ASK order at ' + str(bt.ask_price))
        bt.sell_limit_order('USDT', bt.ask_price, AMOUNT)
    my_telegram_bot.log_telegram(get_buf())
    return 0

def main_loop() :
    while True :
        t0 = time.time()
        #if bt.bithumb.get_balance('USDC')[0] > 1 :
        #    sub_loop_arbibot_1s()
        #    time.sleep(0.5)
        #    continue
        sub_loop_1s()
        t1 = time.time()
        time_elapsed = t1-t0
        if time_elapsed < 1 :
            time.sleep(1-time_elapsed)
        if time.localtime(t0).tm_min != time.localtime().tm_min :
            sub_loop_1m()
            if time.localtime(t0).tm_hour != time.localtime().tm_hour :
                sub_loop_1h()
    return 0

def sub_loop_arbibot_1s() :
    bt.update_orders()
    bt.update_orderbook()
    ub.update_orderbook()

    b_pending = False

    for order_id in bt.order_details :
        order_detail = bt.order_details[order_id]
        if order_detail==None :
            continue
        if not 'data' in order_detail :
            continue
        status = order_detail['data']['order_status']
        price  = float(order_detail['data']['order_price'])
        side   = order_detail['data']['type']
        size   = float(order_detail['data']['order_qty'])
        if status == 'Complete' :
            ub.sell_limit_order('USDT', bt.bid_price, size)
            print_log('bid order at ' + str(price) + ' is complete')
            print_log('ask order at ' + str(ub.bid_price) + ' placed')
        elif status == 'Pending' :
            b_pending = True
            if price >= ub.bid_price :
                bt.cancel_order(order_id)
                print_log('bid order at ' + str(price) + ' is canceled')
                print_log('order_price(='+str(price)+') >= ub_bid_price(='+str(ub.bid_price)+')')
            elif price < bt.bid_price-1 :
                bt.cancel_order(order_id)
                print_log('bid order at ' + str(price) + ' is canceled')
                print_log('order_price(='+str(price)+') < bt_bid_price(='+str(bt.bid_price)+')')
    if not b_pending :
        if bt.bid_price <= ub.bid_price-1 :
            bt.buy_limit_order('USDT', bt.bid_price, 5)
            print_log('bid order at ' + str(bt.bid_price) + ' placed')
            print_log('bt_bid_price = ' + str(bt.bid_price))
            print_log('ub_bid_price = ' + str(ub.bid_price))
    buf = get_buf()
    if len(buf) > 1 :
        my_telegram_bot.log_telegram(buf)
    return 0

def sub_loop_1s() :
    global AMOUNT
    global KP
    global RANGE
    global MIN_HOLD
    global MAX_HOLD
    global HOLD
    global COMPLETE
    #global RANGE_OLD

    bt.update_market_price()
    bt.update_orderbook()
    bt.update_balance()

    #RANGE_OLD = RANGE

    CENTER   = get_CENTER()
    STD      = get_STD()
    KP       = bt.get_kp()
    try:
        RANGE    = get_RANGE(KP, CENTER, STD)
    except:
        print_log("ERROR")
    MIN_HOLD = (5-RANGE)*3 * AMOUNT
    MAX_HOLD = MIN_HOLD + (5*AMOUNT)
    HOLD     = bt.hold_position

    bt.update_orders()
    for order_id in bt.order_details :
        order_detail = bt.order_details[order_id]
        if order_detail==None :
            continue
        if not 'data' in order_detail :
            continue
        status = order_detail['data']['order_status']
        price  = order_detail['data']['order_price']
        side   = order_detail['data']['type']
        size   = order_detail['data']['order_qty']
        COMPLETE = float(price)
        if status == 'Completed' :
            print_log(side + ' order at ' + str(price) + ' is complete')
            for order in bt.orders :
                bt.bithumb.cancel_order(order)
                time.sleep(0.5)
            if HOLD > MIN_HOLD :
                print_log('ASK order at ' + str(COMPLETE+1))
                bt.sell_limit_order('USDT', COMPLETE+1, AMOUNT)
            else :
                print_log('HOLD(='+str(HOLD)+') <= MIN_HOLD(='+str(MIN_HOLD)+')')
            if HOLD < MAX_HOLD :
                print_log('BID order at ' + str(COMPLETE-1))
                bt.buy_limit_order('USDT', COMPLETE-1, AMOUNT)
            else :
                print_log('HOLD(='+str(HOLD)+') <= MAX_HOLD(='+str(MAX_HOLD)+')')
            my_telegram_bot.log_telegram(get_buf())
            break

    #if RANGE_OLD != RANGE :
    #    print_log('RANGE change (' + str(RANGE_OLD) + ' -> ' + str(RANGE) + ')')
    #    if HOLD < MIN_HOLD :
    #        print_log('HOLD(='+str(HOLD)+') < MIN_HOLD(='+str(MIN_HOLD)+')')
    #        print_log('BID order at ' + str(bt.ask_price))
    #        bt.buy_limit_order('USDT', bt.ask_price, AMOUNT)
    #    elif HOLD > MAX_HOLD :
    #        print_log('HOLD(='+str(HOLD)+') > MAX_HOLD(='+str(MAX_HOLD)+')')
    #        print_log('ASK order at ' + str(bt.bid_price))
    #        bt.sell_limit_order('USDT', bt.bid_price, AMOUNT)
    #    my_telegram_bot.log_telegram(get_buf())
    return 0

def sub_loop_1m() :
    global RANGE
    global RANGE_OLD

    kp = bt.get_kp()
    bt.update_candle(kp)
    ma = round(sum(bt.candle[-1440:])/1440, 3)
    bt.update_ma_arr(ma)

    print_log('GRID_STB still alive')
    if RANGE_OLD != RANGE :
        print_log('RANGE change (' + str(RANGE_OLD) + ' -> ' + str(RANGE) + ')')
        if HOLD < MIN_HOLD :
            print_log('HOLD(='+str(HOLD)+') < MIN_HOLD(='+str(MIN_HOLD)+')')
            if len(bt.orders) < 2 :
                print_log('BID order at ' + str(bt.ask_price))
                bt.buy_limit_order('USDT', bt.ask_price, AMOUNT)
            else :
                print_log('Already have both side of orders')
        elif HOLD > MAX_HOLD :
            print_log('HOLD(='+str(HOLD)+') > MAX_HOLD(='+str(MAX_HOLD)+')')
            if len(bt.orders) < 2 :
                print_log('ASK order at ' + str(bt.bid_price))
                bt.sell_limit_order('USDT', bt.bid_price, AMOUNT)
            else :
                print_log('Already have both side of orders')
        if RANGE < RANGE_OLD :
            if bt.hold_position <= AMOUNT*(20-1) :
                print_log('BID order at ' + str(bt.bid_price))
                #bt.buy_limit_order('USDT', bt.bid_price, AMOUNT)
        else :
            if bt.hold_position >= AMOUNT :
                print_log('ASK order at ' + str(bt.ask_price))
                #bt.sell_limit_order('USDT', bt.ask_price, AMOUNT)
        RANGE_OLD = RANGE
        my_telegram_bot.log_telegram(get_buf())
    print_log('KP = ' + str(bt.get_kp()))
    print_log('CENTER = ' + str(get_CENTER()))
    print_log('STD = ' + str(get_STD()))
    print_log('RANGE = ' + str(RANGE))
    print_log('MIN_HOLD = ' + str((5-RANGE)*3*AMOUNT)) 
    print_log('HOLD = ' + str(bt.hold_position))
    print_log('MAX_HOLD = ' + str(((5-RANGE)*3+5)*AMOUNT))
    if time.localtime().tm_min%10 == 0:
        my_telegram_bot.log_telegram(get_buf())
    else :
        get_buf()
    return 0

def sub_loop_1h() :
    return 0

def get_CENTER() :
    ma = round(sum(bt.candle[-1440:])/1440, 3)
    cn = round((max(bt.candle[-1440:])+min(bt.candle[-1440:]))/2, 3)
    return round((ma+cn)/2, 3)

def get_STD() :
    return max(1, round(std(bt.ma_arr), 3))

def get_RANGE(KP, CENTER, STD) :
    if KP > CENTER+2*STD :
        return 5
    elif KP > CENTER+1*STD :
        return 4
    elif KP > CENTER+0*STD :
        return 3
    elif KP > CENTER-1*STD :
        return 2
    elif KP > CENTER-2*STD :
        return 1
    else :
        return 0
    return 0

def main() :
    initialize()
    main_loop()
    return 0

if __name__ == "__main__" :
    main()


