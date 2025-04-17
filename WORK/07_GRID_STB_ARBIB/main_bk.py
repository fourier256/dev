import time
import my_upbit as ub
import my_bithumb as bt
import my_telegram_bot
from my_util import print_log
from my_util import get_buf
from numpy import std

AMOUNT   = 8000
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
    ub.update_balance()
    bt.update_orderbook()
    HOLD = get_HOLD()
    print_log('Start GRID_STB')
    print_log('HOLD = ' + str(HOLD))
    if HOLD <= AMOUNT*(20-1) :
        print_log('BID order at ' + str(bt.bid_price))
        bt.buy_limit_order('USDT', bt.bid_price, AMOUNT)
    if HOLD >= AMOUNT :
        print_log('ASK order at ' + str(bt.ask_price))
        bt.sell_limit_order('USDT', bt.ask_price, AMOUNT)
    my_telegram_bot.log_telegram(get_buf())
    return 0

def main_loop() :
    while True :
        t0 = time.time()
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

def sub_loop_1s() :
    global AMOUNT
    global KP
    global RANGE
    global MIN_HOLD
    global MAX_HOLD
    global HOLD
    global COMPLETE

    bt.update_balance()
    ub.update_balance()
    bt.update_market_price()
    ub.update_orderbook()
    bt.update_orderbook()

    if ub.bid_price > bt.ask_price :
        if ub.hold_position >= 1000 :
            bt.buy_limit_order('USDT', bt.ask_price, 1000)
            ub.sell_limit_order('USDT', bt.bid_price, 1000)
            print_log('Arbitration :')
            print_log(' bt.ask_price = ' + str(bt.ask_price))
            print_log(' ub.bid_price = ' + str(ub.bid_price))
            my_telegram_bot.log_telegram(get_buf())
            time.sleep(1)
            bt.bithumb.withdraw_coin(1000, get_config('WALLET'), 'USDT')

    CENTER   = get_CENTER()
    STD      = get_STD()
    KP       = bt.get_kp()
    RANGE    = get_RANGE(KP, CENTER, STD)
    MIN_HOLD = (5-RANGE)*3 * AMOUNT
    MAX_HOLD = MIN_HOLD + (5*AMOUNT)
    HOLD     = get_HOLD() 

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

    return 0

def sub_loop_1m() :
    global RANGE
    global RANGE_OLD

    kp = bt.get_kp()
    bt.update_candle(kp)
    ma = round(sum(bt.candle[-1440:])/1440, 3)
    bt.update_ma_arr(ma)

    print_log('GRID_STB still alive')
    if int(kp)%2 == 0 :
        # 1 WON Bibration causes too often range changes
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
    print_log('----------')
    print_log('BT_ASK/UB_BID = ' + str(bt.ask_price) + '/' + str(ub.bid_price))
    if time.localtime().tm_min%60 == 0:
        my_telegram_bot.log_telegram(get_buf())
    else :
        get_buf()
    return 0

def sub_loop_1h() :
    return 0

def get_HOLD() :
    return bt.hold_position + ub.hold_position - 10000

def get_CENTER() :
    ma = round(sum(bt.candle[-1440:])/1440, 3)
    cn = round((max(bt.candle[-1440:])+min(bt.candle[-1440:]))/2, 3)
    return round((ma+cn)/2, 3)

def get_STD() :
    return max(2, round(std(bt.ma_arr), 3))

def get_RANGE(KP, CENTER, STD) :
    try :
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
    except :
        return 0
    return 0

def main() :
    initialize()
    main_loop()
    return 0

if __name__ == "__main__" :
    main()


