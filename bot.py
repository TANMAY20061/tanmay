from multiprocessing import Process
from flask import Flask
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    filters,
    ContextTypes,
)
import random

# Flask App Initialization
app = Flask(__name__)

@app.route('/')
def index():
    return "Flask server is running successfully!"

# Function to Start the Flask App
def start_flask():
    app.run(host="0.0.0.0", port=10000)

# Admin Telegram ID and Bot Token
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

# State for ConversationHandler
ENTER_DIGITS = 1

# User data storage
users = {}

# Bot Command Functions
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    user_id = str(user.id)

    if user_id not in users:
        users[user_id] = {"coins": 5, "last_coin_update": update.message.date.strftime("%Y-%m-%d %H:%M:%S")}
        await update.message.reply_text(
            f"Welcome {user.first_name}! You've received 5 free coins as a welcome gift! 🎉"
        )
    else:
        await update.message.reply_text(f"Welcome back {user.first_name}!")

    reply_keyboard = [["📊 PREDICTION", "👤 ACCOUNT"], ["📞 CONTACT ADMIN"]]
    await update.message.reply_text(
        "Welcome to the bot!",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True),
    )

async def add_coins(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("You are not authorized to use this command.")
        return
    try:
        _, user_id, num_coins = update.message.text.split()
        num_coins = int(num_coins)
        users.setdefault(user_id, {"coins": 0, "last_coin_update": "N/A"})
        users[user_id]["coins"] += num_coins
        users[user_id]["last_coin_update"] = update.message.date.strftime("%Y-%m-%d %H:%M:%S")
        await update.message.reply_text(f"Added {num_coins} coins to user {user_id}.")
    except:
        await update.message.reply_text("Error in command format. Use: /coin {userid} {no of coins}")

async def prediction_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = str(update.effective_user.id)
    user_data = users.get(user_id)

    if user_data["coins"] <= 0:
        await update.message.reply_text("Insufficient coins to get a prediction.")
        return ConversationHandler.END

    users[user_id]["coins"] -= 1
    await update.message.reply_text(
        "Successful Connect To The Server ✅\n\n"
        f"💰 Remaining Balance: {users[user_id]['coins']}\n\n"
        "Enter Last 5 Digits:"
    )
    return ENTER_DIGITS

async def provide_prediction(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    period_number = update.message.text
    if not period_number.isdigit() or len(period_number) != 5:
        await update.message.reply_text("Please enter a valid 5-digit number.")
        return ENTER_DIGITS

    index = random.randint(0, 9)
    result, color = RESULTS[index]
    await update.message.reply_text(
        f"🔒 Prediction 🔒\n📅 Period: {period_number}\n💸 Result: {result}\n📥 Colour: {color}\n➡️ Number: {index}"
    )
    return ConversationHandler.END

async def account(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)
    user_data = users.get(user_id, {"coins": 0, "last_coin_update": "N/A"})
    await update.message.reply_text(
        f"👤 Name: {update.effective_user.first_name}\n🆔 User ID: {user_id}\n💵 Balance: ₹ {user_data['coins']}"
    )

async def contact_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("@TANMAYPAUL21")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Prediction cancelled.")
    return ConversationHandler.END

# Function to Start the Bot
def run_bot():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^📊 PREDICTION$"), prediction_start)],
        states={ENTER_DIGITS: [MessageHandler(filters.TEXT & ~filters.COMMAND, provide_prediction)]},
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("coin", add_coins))
    application.add_handler(MessageHandler(filters.Regex("^👤 ACCOUNT$"), account))
    application.add_handler(MessageHandler(filters.Regex("^📞 CONTACT ADMIN$"), contact_admin))

    application.run_polling()

# Main Execution
if __name__ == "__main__":
    flask_process = Process(target=start_flask)
    flask_process.start()
    run_bot()
