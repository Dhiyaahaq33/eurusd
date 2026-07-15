import MetaTrader5 as mt5
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
mt5.initialize()

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
    mt5.order_send({
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

    mt5.order_send({
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

# === MAIN LOOP ===
while True:
    position = get_position()

    # === Manage position
    if position:
        profit = position.profit

        if profit >= PROFIT_TARGET or profit <= MAX_LOSS:
            print(f"Closing trade: {profit}")
            close_position(position)
            time.sleep(2)
            continue

    # === Cooldown
    if time.time() - last_trade_time < COOLDOWN:
        time.sleep(1)
        continue

    # === Indicators
    fast_now = get_ma(5)
    fast_prev = get_ma(5, 1)

    slow_now = get_ma(10)
    slow_prev = get_ma(10, 1)

    trend = get_ma(200)

    price = get_price()

    rates = mt5.copy_rates_from_pos(SYMBOL, TIMEFRAME, 0, 2)
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
