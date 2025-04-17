import time
import numpy as np
import matplotlib.pyplot as plt

import multiprocessing as mp
import threading

import pybithumb
import pyupbit

import my_upbit as ub
import my_bithumb as bt
import my_telegram_bot
from my_util import print_log
from my_util import get_buf

AMOUNT   = 5000
KP       = 0
RANGE    = 0
RANGE_OLD = 0
MIN_HOLD = 0
MAX_HOLD = 0
HOLD     = 0
COMPLETE = 0
RISE_COUNT = 0

def initialize() :
    global COMPLETE
    global RANGE
    global RANGE_OLD
    global wm
    global queue
    global proc
    # update market data
    ub.initialize()
    bt.initialize()
    bt.init_candle(2)
    bt.init_ma_arr()
    bt.update_balance()
    ub.update_balance()
    ub.update_balance_krw()
    bt.update_orderbook()
    ub.update_orderbook()
    # update global variables
    COMPLETE = bt.market_price
    RANGE = get_RANGE(bt.get_kp(), get_CENTER(), get_STD())
    RANGE_OLD = RANGE
    HOLD = get_HOLD()
    # log and initial order
    print_log('Start GRID_STB')
    print_log('HOLD = ' + str(HOLD))
    print_log('TOTAL = ' + str(get_TOTAL_BALANCE()))
    if HOLD > AMOUNT*10 :
        if HOLD <= AMOUNT*(20-1) :
            print_log('BID order at ' + str(bt.bid_price-1))
            bt.buy_limit_order('USDT', bt.bid_price-1, AMOUNT)
        if HOLD >= AMOUNT :
            print_log('ASK order at ' + str(bt.ask_price))
            bt.sell_limit_order('USDT', bt.ask_price, AMOUNT)
    else :
        if HOLD <= AMOUNT*(20-1) :
            print_log('BID order at ' + str(bt.bid_price))
            bt.buy_limit_order('USDT', bt.bid_price, AMOUNT)
        if HOLD >= AMOUNT :
            print_log('ASK order at ' + str(bt.ask_price+1))
            bt.sell_limit_order('USDT', bt.ask_price+1, AMOUNT)
    my_telegram_bot.log_telegram(get_buf())
    draw_plot()
    my_telegram_bot.send_image('graph.png')
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
    global RISE_COUNT

    bt.update_balance()
    ub.update_balance()
    ub.update_balance_krw()
    bt.update_market_price()
    bt.update_orderbook()

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
            if side == 'ask' :
                if RISE_COUNT < 0 :
                    RISE_COUNT = 0
                RISE_COUNT += 1
            else :
                if RISE_COUNT > 0 :
                    RISE_COUNT = 0
                RISE_COUNT -=1
            for order in bt.orders :
                bt.bithumb.cancel_order(order)
                time.sleep(0.5)
            if HOLD > MIN_HOLD :
                if side == 'ask' and RISE_COUNT>0 :
                    print_log('Keep Rising (' + str(RISE_COUNT) +')')
                    print_log('ASK order at ' + str(COMPLETE+2))
                    bt.sell_limit_order('USDT', COMPLETE+2, AMOUNT)
                    time.sleep(0.5)
                else :
                    print_log('ASK order at ' + str(COMPLETE+2))
                    bt.sell_limit_order('USDT', COMPLETE+2, AMOUNT)
                    time.sleep(0.5)
            else :
                print_log('HOLD(='+str(HOLD)+') <= MIN(='+str(MIN_HOLD)+')')
                print_log('ASK order at ' + str(COMPLETE+2))
                bt.sell_limit_order('USDT', COMPLETE+2, AMOUNT)
                time.sleep(0.5)
            if HOLD < MAX_HOLD :
                if side == 'bid' and RISE_COUNT<-0 :
                    print_log('Keep Falling (' + str(RISE_COUNT) +')')
                    print_log('BID order at ' + str(COMPLETE-2))
                    bt.buy_limit_order('USDT', COMPLETE-2, AMOUNT)
	                  time.sleep(0.5)
                else :
                    print_log('BID order at ' + str(COMPLETE-1))
                    bt.buy_limit_order('USDT', COMPLETE-1, AMOUNT)
                    time.sleep(0.5)
            else :
                print_log('HOLD(='+str(HOLD)+') <= MAX(='+str(MAX_HOLD)+')')
                print_log('BID order at ' + str(COMPLETE-2))
                bt.buy_limit_order('USDT', COMPLETE-2, AMOUNT)
                time.sleep(0.5)
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
                print_log('HOLD(='+str(HOLD)+') < MIN(='+str(MIN_HOLD)+')')
                if len(bt.orders) < 2 :
                    print_log('BID order at ' + str(bt.ask_price))
                    bt.buy_limit_order('USDT', bt.ask_price, AMOUNT)
                else :
                    print_log('Already have both side of orders')
            elif HOLD > MAX_HOLD :
                print_log('HOLD(='+str(HOLD)+') > MAX(='+str(MAX_HOLD)+')')
                if len(bt.orders) < 2 :
                    print_log('ASK order at ' + str(bt.bid_price))
                    bt.sell_limit_order('USDT', bt.bid_price, AMOUNT)
                else :
                    print_log('Already have both side of orders')
            RANGE_OLD = RANGE
            my_telegram_bot.log_telegram(get_buf())
    print_log('KP = ' + str(bt.get_kp()))
    print_log('CENTER = ' + str(get_CENTER()))
    print_log('STD = ' + str(get_STD()))
    print_log('RANGE = ' + str(RANGE))
    print_log('MIN_HOLD = ' + str((5-RANGE)*3*AMOUNT)) 
    print_log('HOLD = ' + str(bt.hold_position))
    print_log('MAX_HOLD = ' + str(((5-RANGE)*3+5)*AMOUNT))
    print_log('TOTAL = ' + str(get_TOTAL_BALANCE()))
    #print_log('----------')
    #print_log('ub_bid / bt_ask : ' + str(ub.bid_price) + ' / ' + str(bt.ask_price))
    if time.localtime().tm_min == 0:
        my_telegram_bot.log_telegram(get_buf())
        draw_plot()
        my_telegram_bot.send_image('graph.png')
    else :
        get_buf()
    return 0

def sub_loop_1h() :
    return 0

def get_HOLD() :
    return round(bt.hold_position + ub.hold_position - 10000)

def get_TOTAL_BALANCE() :
    return int((bt.hold_position + ub.hold_position)*bt.market_price + bt.krw + ub.krw)

def get_CENTER() :
    ma = round(sum(bt.candle[-1440:])/1440, 3)
    cn = round((max(bt.candle[-1440:])+min(bt.candle[-1440:]))/2, 3)
    return round((ma+cn)/2, 3)

def get_STD() :
    return max(3, round(np.std(bt.ma_arr), 3))

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

def draw_plot() :
    bt_candle = np.random.uniform(100, 110, 1440) 
    bt_ma_arr = np.random.uniform(100, 110, 1440)
    bt_ma_arr_r1 = np.random.uniform(100, 110, 1440) 
    bt_ma_arr_r2 = np.random.uniform(100, 110, 1440) 
    bt_ma_arr_r3 = np.random.uniform(100, 110, 1440) 
    bt_ma_arr_r4 = np.random.uniform(100, 110, 1440) 

    for i in range(1440) :
        bt_candle[i] = bt.candle[i+1440]
        bt_ma_arr[i] = (bt.ma_arr[i] + (min(bt.candle[i:i+1440])+max(bt.candle[i:i+1440]))/2)/2
        STD = max(2, round(np.std(bt.ma_arr), 3))
        bt_ma_arr_r1[i] = bt_ma_arr[i]-STD*2
        bt_ma_arr_r2[i] = bt_ma_arr[i]-STD*1
        bt_ma_arr_r3[i] = bt_ma_arr[i]+STD*1
        bt_ma_arr_r4[i] = bt_ma_arr[i]+STD*2
    plt.figure(figsize=(12, 6))
    plt.plot(bt_ma_arr, label='bt.ma_arr', color='blue')
    plt.plot(bt_ma_arr_r1, label='bt.ma_arr_r1', color='skyblue')
    plt.plot(bt_ma_arr_r2, label='bt.ma_arr_r2', color='skyblue')
    plt.plot(bt_ma_arr_r3, label='bt.ma_arr_r3', color='skyblue')
    plt.plot(bt_ma_arr_r4, label='bt.ma_arr_r4', color='skyblue')
    plt.plot(bt_candle, label='bt.candle', color='orange')
    plt.title('Graph of bt.candle and bt.ma_arr')
    plt.xlabel('Index')
    plt.ylabel('Value')
    plt.legend()
    plt.grid()
    plt.ylim(min(bt_ma_arr)-10, max(bt_ma_arr)+10)
    plt.savefig('graph.png')
    plt.close()
    return 0

def main() :
    initialize()
    #thread_UB = threading.Thread(target=ws_ub_loop)
    #thread_BT = threading.Thread(target=ws_bt_loop)
    thread_MN = threading.Thread(target=main_loop)
    #thread_UB.start()
    #thread_BT.start()
    thread_MN.start()
    #thread_UB.join()
    #thread_BT.join()
    thread_MN.join()
    return 0

if __name__ == "__main__" :
    main()



