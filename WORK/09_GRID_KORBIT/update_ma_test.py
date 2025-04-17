import time
import my_upbit as ub
import my_bithumb as bt
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
            print(bt.candle[2870:2880])
            if time.localtime().tm_min%20 == 0:
                break
    return 0

def sub_loop_1s() :
    bt.update_market_price()
    return 0

def sub_loop_1m() :
    kp = bt.get_kp()
    bt.update_candle(kp)
    ma = round(sum(bt.candle[-1440:])/1440, 3)
    bt.update_ma_arr(ma)
    return 0

def main() :
    initialize()
    main_loop()
    #print(bt.candle[0:10])
    print(bt.candle[2860:2880])
    #print(bt.ma_arr[0:10])
    #print(bt.ma_arr[1430:1440])

    bt.candle = []
    bt.ma_arr = []
    initialize()
    #print(bt.candle[0:10])
    print(bt.candle[2860:2880])
    #print(bt.ma_arr[0:10])
    #print(bt.ma_arr[1430:1440])

    return 0

if __name__ == "__main__" :
    main()


