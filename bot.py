import datetime
from multiprocessing import Process
from flask import Flask
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# Flask App Initialization
app = Flask(__name__)

@app.route('/')
def index():
    return "Flask server is running successfully!"

# Function to Start the Flask App
def start_flask():
    app.run(host="0.0.0.0", port=10000)

# Admin Telegram ID and Bot Token
ADMIN_ID = 5181364124
BOT_TOKEN = "7907519932:AAHlCi3QZuAp6HaDzE27S6LqYTYDBiwO_a8"  # Replace with your actual bot token

# User data storage
users = {}

# Function to calculate period number and result
def calculate_period_and_result():
    now = datetime.datetime.utcnow()
    offset_minutes = 330  # Offset for timezone (5 hours 30 minutes)
    total_minutes = now.hour * 60 + now.minute - offset_minutes

    period_calculation = 10001 + total_minutes
    period_number = now.strftime("%Y%m%d") + str(period_calculation)

    # Calculate digit sum
    digit_sum = sum(int(digit) for digit in str(period_calculation))
    result_number = (digit_sum * 7) % 10
    result = "SMALL" if 1 <= result_number <= 4 else "BIG"
    return period_number, result

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

async def deduct_coins(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("You are not authorized to use this command.")
        return
    try:
        _, user_id, num_coins = update.message.text.split()
        num_coins = int(num_coins)
        if user_id in users and users[user_id]["coins"] >= num_coins:
            users[user_id]["coins"] -= num_coins
            users[user_id]["last_coin_update"] = update.message.date.strftime("%Y-%m-%d %H:%M:%S")
            await update.message.reply_text(f"Deducted {num_coins} coins from user {user_id}.")
        else:
            await update.message.reply_text(f"Insufficient coins or user {user_id} does not exist.")
    except:
        await update.message.reply_text("Error in command format. Use: /discoin {userid} {no of coins}")

async def view_all_users(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("You are not authorized to use this command.")
        return
    if not users:
        await update.message.reply_text("No users found.")
        return
    user_details = "\n".join(
        f"🆔 {user_id}: 💰 {data['coins']} coins (Last update: {data['last_coin_update']})"
        for user_id, data in users.items()
    )
    await update.message.reply_text(f"All Users:\n{user_details}")

async def prediction(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)
    user_data = users.get(user_id)

    if user_data["coins"] <= 0:
        await update.message.reply_text("Insufficient coins to get a prediction.")
        return

    users[user_id]["coins"] -= 1
    period_number, result = calculate_period_and_result()
    await update.message.reply_text(
        f"🔒 Prediction 🔒\n"
        f"📅 Period: {period_number}\n"
        f"💸 Result: {result}\n"
        f"💰 Remaining Balance: {users[user_id]['coins']}"
    )

async def account(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)
    user_data = users.get(user_id, {"coins": 0, "last_coin_update": "N/A"})
    await update.message.reply_text(
        f"👤 Name: {update.effective_user.first_name}\n"
        f"🆔 User ID: {user_id}\n"
        f"💵 Balance: ₹ {user_data['coins']}\n"
        f"📅 Last Coin Update: {user_data['last_coin_update']}"
    )

async def contact_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("@TANMAYPAUL21")

# Function to Start the Bot
def run_bot():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("coin", add_coins))
    application.add_handler(CommandHandler("discoin", deduct_coins))
    application.add_handler(CommandHandler("allusers", view_all_users))
    application.add_handler(MessageHandler(filters.Regex("^📊 PREDICTION$"), prediction))
    application.add_handler(MessageHandler(filters.Regex("^👤 ACCOUNT$"), account))
    application.add_handler(MessageHandler(filters.Regex("^📞 CONTACT ADMIN$"), contact_admin))

    application.run_polling()

# Main Execution
if __name__ == "__main__":
    flask_process = Process(target=start_flask)
    flask_process.start()
    run_bot()
