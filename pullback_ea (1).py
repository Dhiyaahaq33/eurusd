import MetaTrader5 as mt5
import sys
import time

# === SETTINGS ===
LOT_SIZE = 0.01
STOP_LOSS_PIPS = 10
TAKE_PROFIT_PIPS = 25

PROFIT_TARGET = 0.50
MAX_LOSS = -0.30

SYMBOL = "EURUSD"
TIMEFRAME = mt5.TIMEFRAME_M15

# === CONNECT ===
if not mt5.initialize():
    print(f"MT5 initialize() failed, error code: {mt5.last_error()}")
    sys.exit(1)

last_trade_time = 0
COOLDOWN = 180  # seconds

def get_ma(period, shift=0):
    rates = mt5.copy_rates_from_pos(SYMBOL, TIMEFRAME, shift, period + 1)
    closes = [r['close'] for r in rates]
    return sum(closes[-period:]) / period

def get_price():
    tick = mt5.symbol_info_tick(SYMBOL)
    return tick.ask

def get_position():
    positions = mt5.positions_get(symbol=SYMBOL)
    return positions[0] if positions else None

def close_position(position):
    price = mt5.symbol_info_tick(SYMBOL).bid
    result = mt5.order_send({
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": SYMBOL,
        "volume": position.volume,
        "type": mt5.ORDER_TYPE_SELL if position.type == 0 else mt5.ORDER_TYPE_BUY,
        "position": position.ticket,
        "price": price,
        "deviation": 10,
        "magic": 123456,
        "comment": "Close trade"
    })
    if result is None or result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"Close order FAILED for ticket {position.ticket}: {result}")
        return False
    return True

def open_trade(order_type):
    price = get_price()
    point = mt5.symbol_info(SYMBOL).point

    if order_type == "BUY":
        sl = price - STOP_LOSS_PIPS * point
        tp = price + TAKE_PROFIT_PIPS * point
        order_type_mt5 = mt5.ORDER_TYPE_BUY
    else:
        sl = price + STOP_LOSS_PIPS * point
        tp = price - TAKE_PROFIT_PIPS * point
        order_type_mt5 = mt5.ORDER_TYPE_SELL

    result = mt5.order_send({
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": SYMBOL,
        "volume": LOT_SIZE,
        "type": order_type_mt5,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": 10,
        "magic": 123456,
        "comment": "Pullback EA"
    })
    if result is None or result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"Open order FAILED ({order_type}): {result}")
        return False
    return True

# === MAIN LOOP ===
while True:
    position = get_position()

    # === Manage position
    if position:
        profit = position.profit

        if profit >= PROFIT_TARGET or profit <= MAX_LOSS:
            print(f"Closing trade: {profit}")
            close_position(position)  # retry next loop iteration if this failed
            time.sleep(2)
            continue

    # === Cooldown
    if time.time() - last_trade_time < COOLDOWN:
        time.sleep(1)
        continue

    # === Indicators (based on the last CLOSED candle, shift=1, to avoid repainting
    # off the still-forming current bar)
    fast_now = get_ma(5, 1)
    fast_prev = get_ma(5, 2)

    slow_now = get_ma(10, 1)
    slow_prev = get_ma(10, 2)

    trend = get_ma(200, 1)

    price = get_price()

    rates = mt5.copy_rates_from_pos(SYMBOL, TIMEFRAME, 1, 2)
    close = rates[0]['close']
    prev_close = rates[1]['close']

    # === Conditions
    uptrend = price > trend
    downtrend = price < trend

    pullback_buy = (
        uptrend and
        fast_prev > slow_prev and
        fast_now < slow_now and
        close > prev_close
    )

    pullback_sell = (
        downtrend and
        fast_prev < slow_prev and
        fast_now > slow_now and
        close < prev_close
    )

    # === Execute
    if not position:
        if pullback_buy:
            print("BUY opened")
            open_trade("BUY")
            last_trade_time = time.time()

        elif pullback_sell:
            print("SELL opened")
            open_trade("SELL")
            last_trade_time = time.time()

    time.sleep(2)
