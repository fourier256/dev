import time
import my_upbit as ub
import my_bithumb as bt
import my_telegram_bot

bt.initialize()
ub.initialize()

#for i in range(10) :
while True:
    ub.update_orderbook()
    bt.update_orderbook()
    print(str(ub.bid_price) + ' / ' + str(bt.bid_price))
    if ub.bid_price > bt.bid_price :
        my_telegram_bot.log_telegram((str(ub.bid_price) + ' / ' + str(bt.bid_price)))
    time.sleep(10)
