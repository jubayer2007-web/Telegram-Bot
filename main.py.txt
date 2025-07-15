import telebot
import ccxt
import pandas as pd
import datetime
import pytz
import pandas_ta as pta
import matplotlib.pyplot as plt
import mplfinance as mpf
from candle_patterns import detect_candle_patterns

# === BOT CONFIGURATION ===
TELEGRAM_TOKEN = '7629127338:AAE4ElnTkXsCP6kQ3d9kCRk1UUmd5ScfZUQ'
bot = telebot.TeleBot(TELEGRAM_TOKEN)
exchange = ccxt.binance()

# === UT BOT ALERTS FUNCTION ===
def calculate_ut_bot(df, atr_period=10, key_value=1):
    df['ATR'] = pta.atr(df['High'], df['Low'], df['Close'], length=atr_period)
    src = df['Close']
    nLoss = key_value * df['ATR']
    trailing_stop = pd.Series(index=df.index, dtype=float)
    position = pd.Series(index=df.index, dtype=int)
    buy = pd.Series(False, index=df.index)
    sell = pd.Series(False, index=df.index)

    trailing_stop.iloc[0] = src.iloc[0]
    position.iloc[0] = 0

    for i in range(1, len(df)):
        prev_stop = trailing_stop.iloc[i-1]
        prev_close = src.iloc[i-1]
        close = src.iloc[i]
        loss = nLoss.iloc[i]
        if close > prev_stop and prev_close > prev_stop:
            trailing_stop.iloc[i] = max(prev_stop, close - loss)
        elif close < prev_stop and prev_close < prev_stop:
            trailing_stop.iloc[i] = min(prev_stop, close + loss)
        elif close > prev_stop:
            trailing_stop.iloc[i] = close - loss
        else:
            trailing_stop.iloc[i] = close + loss

        if prev_close < prev_stop and close > trailing_stop.iloc[i]:
            position.iloc[i] = 1; buy.iloc[i] = True
        elif prev_close > prev_stop and close < trailing_stop.iloc[i]:
            position.iloc[i] = -1; sell.iloc[i] = True
        else:
            position.iloc[i] = position.iloc[i-1]

    df['UT_Buy'], df['UT_Sell'] = buy, sell
    return df

# === CHART GENERATION ===
def generate_chart(df, symbol):
    df2 = df.copy()
    df2.index = pd.to_datetime(df2['Timestamp'], unit='ms')
    df2 = df2[['Open','High','Low','Close','Volume']].astype(float)
    mpf.plot(df2.tail(60), type='candle', volume=True,
             style='charles', mav=(20),
             title=f'{symbol} 4H Chart',
             savefig=f'{symbol}_chart.png')

# === SIGNAL & ANALYSIS FUNCTION ===
def analyze_symbol(symbol):
    try:
        bars = exchange.fetch_ohlcv(symbol, timeframe='4h', limit=100)
    except Exception as e:
        return None
    df = pd.DataFrame(bars, columns=['Timestamp','Open','High','Low','Close','Volume'])

    df = calculate_ut_bot(df)
    df['RSI'] = pta.rsi(df['Close'], length=14)
    macd = pta.macd(df['Close'])
    df['MACD'], df['MACD_signal'] = macd['MACD_12_26_9'], macd['MACDs_12_26_9']
    df['Stoch'] = pta.stoch(df['High'], df['Low'], df['Close'])['STOCHk_14_3_3']
    df['EMA20'] = pta.ema(df['Close'], length=20)
    df['SAR'] = pta.psar(df['High'], df['Low'], df['Close'])['PSARl_0.02_0.2']
    df['ATR'] = pta.atr(df['High'], df['Low'], df['Close'], length=14)

    last = df.iloc[-1]
    current = last['Close']
    entry = round(current,5)
    sl = round(entry - 2 * last['ATR'],5)
    tp = round(entry + 3 * last['ATR'],5)
    gain = round((tp-entry)/entry*100,2)

    now = datetime.datetime.now(pytz.timezone('US/Eastern'))
    date_str = now.strftime('%Y-%m-%d')
    time_str = now.strftime('%I:%M %p EST')
    move_hours = 6
    target_end = (now + datetime.timedelta(hours=8)).strftime('%I:%M %p EST')
    time_window = f"{(now + datetime.timedelta(hours=6)).strftime('%I:%M %p EST')} – {target_end}"

    ut_buy = last['UT_Buy']
    ut_sell = last['UT_Sell']
    signal_label = "✅ BUY SIGNAL CONFIRMED" if ut_buy else ("❌ BEARISH — AVOID ENTRY" if ut_sell else "⚠️ NO CLEAR SIGNAL")

    candle_matches = detect_candle_patterns(df[['Open','High','Low','Close']].tail(5))
    candle_text = "\n📊 Candle Pattern:\n" + "\n".join([f"🔹 {p}" for p in candle_matches]) if candle_matches else ""

    text = f"""📡 #Signal | 🪙 {symbol} | ⏱️ 4H Chart
📅 Date: {date_str} | 🕒 Signal Time: {time_str}

📊 Indicators:
🔹 RSI: {last['RSI']:.2f}
🔹 MACD: {'Bullish' if last['MACD'] > last['MACD_signal'] else 'Bearish'}
🔹 Stochastic: {last['Stoch']:.2f}
🔹 EMA20: {last['EMA20']:.5f}
🔹 SAR: {last['SAR']:.5f}
🔹 ATR: {last['ATR']:.5f}
{candle_text}

{signal_label}
"""
    if ut_buy:
        text += f"\n📥 Entry: {entry}\n🛑 Stop Loss: {sl}\n🎯 Target: {tp}\n📈 Estimated Gain: +{gain}%\n"

    text += f"\n⏱ Expected Move: {move_hours} hours\n🕒 Target Time (EST): {time_window}"

    generate_chart(df, symbol.replace("/",""))
    return text, f"{symbol.replace('/','')}_chart.png"

# === TELEGRAM BOT HANDLERS ===
@bot.message_handler(commands=['start'])
def send_welcome(msg):
    bot.reply_to(msg,
        "👋 Welcome to Binance Premium Spot Signal Bot!\n\nSend symbol like `DOGEUSDT` to get analysis.",
        parse_mode='Markdown'
    )

@bot.message_handler(func=lambda m: True)
def handle_symbol(m):
    sym = m.text.strip().upper()
    if not sym.endswith("USDT"):
        sym = sym.replace("/","") + "USDT"
    res = analyze_symbol(sym)
    if not res:
        return bot.reply_to(m, "❌ Invalid symbol or Binance API error.")
    text, img = res
    bot.send_photo(m.chat.id, open(img, 'rb'))
    bot.send_message(m.chat.id, text, parse_mode='Markdown')

print("🤖 Bot is running...")
bot.polling()
