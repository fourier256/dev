import my_bithumb as bt
import my_binance as bn

EXCHANGE = 1400

def main_loop() :
    bt.capture_orderbook()
    ub.capture_orderbook()

    KP_BUY['USDT']  = bt.ask_price['USDT']/EXCHANGE
    KP_SELL['USDT'] = bt.bid_price['USDT']/EXCHANGE
    for symbol in symbols :
        