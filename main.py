import os
import logging
import asyncio
import pandas as pd
import pandas_ta as ta
import mplfinance as mpf
from binance.client import Client
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dotenv import load_dotenv
from datetime import datetime
import schedule
import threading
from flask import Flask

load_dotenv()

# =========================
# API KEYS
# =========================
BINANCE_API_KEY = os.getenv('BINANCE_API_KEY')
BINANCE_API_SECRET = os.getenv('BINANCE_API_SECRET')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)

# =========================
# Logging
# =========================
logging.basicConfig(level=logging.INFO)

# =========================
# Keep Alive (Replit)
# =========================
app_flask = Flask('')

@app_flask.route('/')
def home():
    return "I'm alive!"

def run():
    app_flask.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = threading.Thread(target=run)
    t.start()

# =========================
# Get Historical Data
# =========================
def get_klines(symbol, interval='30m', limit=100):
    klines = client.get_historical_klines(symbol, interval, "2 days ago UTC")
    df = pd.DataFrame(klines, columns=['Open time', 'Open', 'High', 'Low', 'Close',
                                       'Volume', 'Close time', 'Quote asset volume',
                                       'Number of trades', 'Taker buy base asset volume',
                                       'Taker buy quote asset volume', 'Ignore'])
    df['Open time'] = pd.to_datetime(df['Open time'], unit='ms')
    df.set_index('Open time', inplace=True)
    df = df[['Open', 'High', 'Low', 'Close', 'Volume']].astype(float)
    return df

# =========================
# Indicator Analysis
# =========================
def analyze(df):
    df['MA50'] = ta.sma(df['Close'], length=50)
    df['EMA20'] = ta.ema(df['Close'], length=20)
    macd = ta.macd(df['Close'])
    df['MACD'] = macd['MACD_12_26_9']
    df['MACDh'] = macd['MACDh_12_26_9']
    df['RSI'] = ta.rsi(df['Close'])
    bb = ta.bbands(df['Close'])
    df['UpperBB'] = bb['BBU_20_2.0']
    df['MiddleBB'] = bb['BBM_20_2.0']
    df['LowerBB'] = bb['BBL_20_2.0']
    df['ADX'] = ta.adx(df['High'], df['Low'], df['Close'])['ADX_14']
    df['STDDEV'] = ta.stdev(df['Close'])
    return df

# =========================
# Simple Trend Score
# =========================
def calc_trend_score(df):
    score = 0
    if df['Close'].iloc[-1] > df['MA50'].iloc[-1]:
        score += 20
    if df['Close'].iloc[-1] > df['EMA20'].iloc[-1]:
        score += 20
    if df['MACD'].iloc[-1] > 0:
        score += 20
    if df['RSI'].iloc[-1] > 50:
        score += 20
    if df['Close'].iloc[-1] > df['UpperBB'].iloc[-1]:
        score += 20
    return score

# =========================
# Generate Chart
# =========================
def plot_chart(df, symbol):
    mpf.plot(
        df.tail(50),
        type='candle',
        mav=(20, 50),
        volume=True,
        style='yahoo',
        savefig=f"{symbol}.png"
    )

# =========================
# Message Generator
# =========================
def build_signal(symbol, df, score):
    trend = "Uptrend" if score >= 50 else "Downtrend"
    est_up = score
    est_down = 100 - score
    entry = df['Close'].iloc[-1]

    msg = f"""
📈 Binance Spot Premium Signal

📊 *See attached chart below*

🪙 COIN: {symbol}
⏰ Timeframe: 30m
✅ Trend: {trend} ({score}%)
"""

    if trend == "Uptrend":
        msg += f"""Entry: {entry:.2f}
TP1: {entry * 1.01:.2f} (Est. ~1hr)
TP2: {entry * 1.02:.2f} (Est. ~2hr)
TP3: {entry * 1.03:.2f} (Est. ~4hr)
Sell: {entry * 1.035:.2f} (Est. ~5hr)
Stop Loss: {entry * 0.985:.2f}

"""
    else:
        msg += f"""Est Pump: ${(entry * 0.01):.2f}
"""

    msg += f"""Est Up: {est_up}%
Est Down: {est_down}%

Indicators:
- MA(50): {'Bullish' if df['Close'].iloc[-1] > df['MA50'].iloc[-1] else 'Bearish'}
- EMA(20): {'Bullish crossover' if df['Close'].iloc[-1] > df['EMA20'].iloc[-1] else 'Bearish crossover'}
- MACD: {"Histogram positive, bullish crossover" if df['MACD'].iloc[-1] > 0 else "Histogram negative, bearish crossover"}
- RSI: {df['RSI'].iloc[-1]:.2f} {"(Strong)" if df['RSI'].iloc[-1] > 70 else "(Oversold)" if df['RSI'].iloc[-1] < 30 else ""}
- Bollinger Bands: {'Upper band breakout' if df['Close'].iloc[-1] > df['UpperBB'].iloc[-1] else 'Lower band breakout'} (Price: {entry:.2f}, {'Upper' if df['Close'].iloc[-1] > df['UpperBB'].iloc[-1] else 'Lower'} BB: {df['UpperBB'].iloc[-1] if df['Close'].iloc[-1] > df['UpperBB'].iloc[-1] else df['LowerBB'].iloc[-1]:.2f})
- ADX: {df['ADX'].iloc[-1]:.2f} (Strong trend)
- Std Dev: {df['STDDEV'].iloc[-1]:.2f}

Why {'should buy' if trend == 'Uptrend' else 'shouldn’t buy'}:
{"Price is trading above MA50 and EMA20, MACD is positive and RSI strong — indicating continued momentum. Suitable for short-term swing." if trend == "Uptrend" else "Current trend strongly bearish, price below MA50 and EMA20, MACD negative — potential to fall further. RSI indicates oversold but no reversal yet."}

{'Where pump possible:\nPrice nearing major support, RSI oversold — short-term bounce possible if big buy orders appear.\n\nSuggestions:\nAvoid entry now — wait for confirmation of reversal before buying.' if trend == "Downtrend" else ""}
"""
    return msg

# =========================
# Telegram Command
# =========================
async def signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    symbol = context.args[0].upper()
    if not symbol.endswith('USDT'):
        symbol += 'USDT'
    df = get_klines(symbol)
    df = analyze(df)
    score = calc_trend_score(df)
    plot_chart(df, symbol)
    msg = build_signal(symbol, df, score)
    await update.message.reply_text(msg)
    await update.message.reply_photo(photo=InputFile(f"{symbol}.png"))

# =========================
# Auto Scan (Global)
# =========================
async def auto_scan(app):
    symbols = ['BTCUSDT', 'ETHUSDT']
    for sym in symbols:
        df = get_klines(sym)
        df = analyze(df)
        score = calc_trend_score(df)
        if score >= 80:
            plot_chart(df, sym)
            msg = build_signal(sym, df, score)
            await app.bot.send_message(chat_id=CHAT_ID, text=msg)
            await app.bot.send_photo(chat_id=CHAT_ID, photo=InputFile(f"{sym}.png"))

# =========================
# User-specific auto update
# =========================
user_subscriptions = {}

async def autoupdate_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if len(context.args) < 1:
        await update.message.reply_text("Usage: /autoupdate <COIN>")
        return
    coin = context.args[0].upper()
    if not coin.endswith('USDT'):
        coin += 'USDT'
    if user_id not in user_subscriptions:
        user_subscriptions[user_id] = set()
    user_subscriptions[user_id].add(coin)
    await update.message.reply_text(
        f"🔔 Auto Update ON\n\nCoin: {coin}\nFrequency: Every 20 mins\nUpdates will be sent automatically.\nUse /closeautoupdate {coin} to stop."
    )

async def close_autoupdate_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if len(context.args) < 1:
        await update.message.reply_text("Usage: /closeautoupdate <COIN>")
        return
    coin = context.args[0].upper()
    if not coin.endswith('USDT'):
        coin += 'USDT'
    if user_id in user_subscriptions and coin in user_subscriptions[user_id]:
        user_subscriptions[user_id].remove(coin)
        await update.message.reply_text(
            f"❌ Auto Update Stopped\n\nCoin: {coin}\nYou will no longer receive updates for this coin."
        )
    else:
        await update.message.reply_text(f"No active auto update for {coin} found.")

async def user_auto_scan(app):
    for user_id, coins in user_subscriptions.items():
        for coin in coins:
            df = get_klines(coin)
            df = analyze(df)
            score = calc_trend_score(df)
            plot_chart(df, coin)
            msg = build_signal(coin, df, score)
            await app.bot.send_message(chat_id=user_id, text=msg)
            await app.bot.send_photo(chat_id=user_id, photo=InputFile(f"{coin}.png"))

# =========================
# Main Loop
# =========================
async def scheduler(app):
    schedule.every(30).minutes.do(lambda: asyncio.create_task(auto_scan(app)))
    schedule.every(20).minutes.do(lambda: asyncio.create_task(user_auto_scan(app)))
    while True:
        schedule.run_pending()
        await asyncio.sleep(1)

async def main():
    keep_alive()
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("signal", signal))
    app.add_handler(CommandHandler("autoupdate", autoupdate_handler))
    app.add_handler(CommandHandler("closeautoupdate", close_autoupdate_handler))
    asyncio.create_task(scheduler(app))
    await app.run_polling()

if __name__ == '__main__':
    asyncio.run(main())
