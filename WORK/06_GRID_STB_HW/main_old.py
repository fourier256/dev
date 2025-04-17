import my_bithumb as bt
import time
import my_telegram_bot
from my_util import print_log
import pickle

def initialize() :
    bt.initialize()
    bt.update_balance()
    bt.update_orderbook()
    for idx in range(10) :
        if (idx+1)*10000 < bt.hold_position :
            print('sell at ' + str(bt.ask_price+idx))
            bt.sell_limit_order('USDT', bt.ask_price+idx, 10000)
            time.sleep(0.5)
        if idx*10000 <= (150000-bt.hold_position) :
            print('buy at ' + str(bt.bid_price-idx-1))
            bt.buy_limit_order('USDT', bt.bid_price-idx-1, 10000)
            time.sleep(0.5)
    return 0

def main_loop() :
    while True:
        tt = time.time()
        bt.update_orders()
        for order_id in bt.order_details :
            order_detail = bt.order_details[order_id]
            if order_detail == None :
                continue
            status = order_detail['data']['order_status']
            side   = order_detail['data']['type']
            price  = int(order_detail['data']['order_price'])
            if order_detail['data']['order_status'] == 'Completed' :
                if side == 'bid' :
                    bt.sell_limit_order('USDT', price+1, 10000)
                    my_telegram_bot.log_telegram('buy order at ' + str(price) + 'is completed. \nplace sell order at ' + str(price+1) + '.')
                    with open('data.pkl', 'wb') as f:
                        pickle.dump(bt.orders, f)
                else :
                    bt.buy_limit_order('USDT', price-1, 10000)
                    my_telegram_bot.log_telegram('sell order at ' + str(price) + 'is completed. \nplace buy order at ' + str(price-1) + '.')
                    with open('data.pkl', 'wb') as f:
                        pickle.dump(bt.orders, f)
        time.sleep(0.5)
        if time.localtime().tm_min != time.localtime(tt).tm_min :
            print('min_event')
            if time.localtime().tm_hour != time.localtime(tt).tm_hour :
                for order in bt.orders :
                    bt.bithumb.cancel_order(order)
                    time.sleep(0.5)
                for idx in range(10) :
                    if (idx+1)*10000 < bt.hold_position :
                        print('sell at ' + str(bt.ask_price+idx))
                        bt.sell_limit_order('USDT', bt.ask_price+idx, 10000)
                        time.sleep(0.5)
                    if idx*10000 <= (100000-bt.hold_position) :
                        print('buy at ' + str(bt.bid_price-idx-1))
                        bt.buy_limit_order('USDT', bt.bid_price-idx-1, 10000)
                        time.sleep(0.5)
    return 0

def main() :
    initialize()
    main_loop()
    return 0

if __name__ == "__main__":
    main()
