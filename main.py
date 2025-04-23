
import yfinance as yf
import ta
from telegram import Bot, Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext

bot_token = '8036468495:AAEc5BBOjvzC-nTkqKpazuU5HxHbzYFhgtw'
chat_id = '5484692253'
bot = Bot(token=bot_token)

def get_signal(update: Update, context: CallbackContext):
    pair = update.message.text.upper().replace("/", "") + "=X"
    data = yf.download(pair, interval="5m", period="1d")

    if data.empty:
        update.message.reply_text("ডেটা পাওয়া যায়নি। পেয়ারটি চেক করুন।")
        return

    data['RSI'] = ta.momentum.RSIIndicator(data['Close'], window=14).rsi()
    data['EMA20'] = ta.trend.EMAIndicator(data['Close'], window=20).ema_indicator()
    data['Bullish'] = (data['Open'] < data['Close']) & (data['Open'].shift(1) > data['Close'].shift(1))
    data['Bearish'] = (data['Open'] > data['Close']) & (data['Open'].shift(1) < data['Close'].shift(1))

    last_rsi = data['RSI'].iloc[-1]
    last_price = data['Close'].iloc[-1]
    last_ema = data['EMA20'].iloc[-1]
    bullish = data['Bullish'].iloc[-1]
    bearish = data['Bearish'].iloc[-1]

    if last_rsi < 30 and last_price > last_ema and bullish:
        signal = "Strong Buy"
    elif last_rsi > 70 and last_price < last_ema and bearish:
        signal = "Strong Sell"
    else:
        signal = "No Strong Signal"

    message = f"{pair.replace('=X','')}
Price: {last_price:.4f}
RSI: {last_rsi:.2f}
EMA20: {last_ema:.4f}
Signal: {signal}"
    update.message.reply_text(message)

updater = Updater(token=bot_token, use_context=True)
dispatcher = updater.dispatcher
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, get_signal))
updater.start_polling()
