from flask import Flask
from threading import Thread
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    filters,
    ContextTypes,
)
import random
import os

# Admin Telegram ID
ADMIN_ID = 7163028849
BOT_TOKEN = "8022705558:AAFIkcDxK0w2HtkXfPKlraQRTqK4L63Mg-o"  # Replace with your actual bot token

# Prediction results
RESULTS = [
    ("SMALL RED", "🔴"),
    ("SMALL GREEN", "🟢"),
    ("BIG RED", "🔴"),
    ("BIG GREEN", "🟢"),
    ("SMALL RED", "🔴"),
    ("BIG GREEN", "🟢"),
    ("SMALL GREEN", "🟢"),
    ("BIG RED", "🔴"),
    ("SMALL RED", "🔴"),
    ("BIG GREEN", "🟢"),
]

ENTER_DIGITS = 1
users = {}

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    user_id = str(user.id)
    if user_id not in users:
        users[user_id] = {"coins": 5, "last_coin_update": update.message.date.strftime("%Y-%m-%d %H:%M:%S")}
        await update.message.reply_text(f"Welcome {user.first_name}! You've received 5 free coins!")
    else:
        await update.message.reply_text(f"Welcome back {user.first_name}!")

    reply_keyboard = [["📊 PREDICTION", "👤 ACCOUNT"], ["📞 CONTACT ADMIN"]]
    await update.message.reply_text(
        "Welcome to the bot!",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True),
    )

# Add other handlers and bot logic here...

def run_bot():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    # Add other handlers as necessary...
    application.run_polling()

# Flask server for keep-alive
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

# Start bot in a separate thread
if __name__ == "__main__":
    Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
