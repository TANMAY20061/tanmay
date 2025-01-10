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

# Admin Telegram ID
ADMIN_ID = 5181364124
BOT_TOKEN = "7907519932:AAHlCi3QZuAp6HaDzE27S6LqYTYDBiwO_a8"  # Replace with your actual bot token

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

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    user_id = str(user.id)

    if user_id not in users:
        # If the user is new, add them to the users dictionary and give 5 free coins
        users[user_id] = {"coins": 5, "last_coin_update": update.message.date.strftime("%Y-%m-%d %H:%M:%S")}
        await update.message.reply_text(
            f"Welcome {user.first_name}! You've received 5 free coins as a welcome gift! 🎉"
        )
    else:
        # If the user already exists, send a normal greeting
        await update.message.reply_text(f"Welcome back {user.first_name}!")

    # Display the main menu
    reply_keyboard = [["📊 PREDICTION", "👤 ACCOUNT"], ["📞 CONTACT ADMIN"]]
    await update.message.reply_text(
        "Welcome to the bot!",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True),
    )

# Add coins command
async def add_coins(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("You are not authorized to use this command.")
        return

    try:
        _, user_id, num_coins = update.message.text.split()
        user_id = user_id.strip()
        num_coins = int(num_coins)

        if user_id not in users:
            # If user doesn't exist, add them to the users dictionary
            users[user_id] = {"coins": 0, "last_coin_update": "N/A"}

        users[user_id]["coins"] += num_coins
        users[user_id]["last_coin_update"] = update.message.date.strftime("%Y-%m-%d %H:%M:%S")
        await update.message.reply_text(f"Added {num_coins} coins to user {user_id}.")
    except Exception:
        await update.message.reply_text("Error in command format. Use: /coin {userid} {no of coins}")

# Prediction handler
async def prediction_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = str(update.effective_user.id)
    user_data = users.get(user_id)

    if user_data["coins"] <= 0:
        await update.message.reply_text("Insufficient coins to get a prediction.")
        return ConversationHandler.END

    # Deduct one coin
    users[user_id]["coins"] -= 1

    await update.message.reply_text(
        "Successful Connect To The Server ✅\n\n"
        "✅ You have successfully used this command! 1 coin has been deducted from your account.\n\n"
        f"💰 Remaining Balance: {users[user_id]['coins']}\n\n"
        "Enter Last 5 Digits:"
    )
    return ENTER_DIGITS

# Handle digit input and provide prediction
async def provide_prediction(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    period_number = update.message.text
    if not period_number.isdigit() or len(period_number) != 5:
        await update.message.reply_text("Please enter a valid 5-digit number.")
        return ENTER_DIGITS

    # Generate random result
    index = random.randint(0, 9)
    result, color = RESULTS[index]

    await update.message.reply_text(
        "🔒 1 Minute Prediction 🔒\n\n"
        f"📅 Period: {period_number}\n\n"
        f"💸 Result: {result}\n\n"
        f"📥 Colour: {color}\n\n"
        f"➡️ Number: {index}"
    )
    return ConversationHandler.END

# Account information handler
async def account(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)
    user_data = users.get(user_id, {"coins": 0, "last_coin_update": "N/A"})

    await update.message.reply_text(
        f"👤 Name: {update.effective_user.first_name}\n"
        f"🆔 User ID: {user_id}\n\n"
        f"💵 Balance: ₹ {user_data['coins']}\n\n"
        f"⌚️ Last Update: {user_data['last_coin_update']}\n"
    )

# Contact admin handler
async def contact_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("@TANMAYPAUL21")

# Cancel handler
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Prediction cancelled.")
    return ConversationHandler.END

# Main function
def main() -> None:
    # Initialize the bot
    application = Application.builder().token(BOT_TOKEN).build()

    # Conversation handler
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^📊 PREDICTION$"), prediction_start)],
        states={
            ENTER_DIGITS: [MessageHandler(filters.TEXT & ~filters.COMMAND, provide_prediction)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # Add handlers
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("coin", add_coins))
    application.add_handler(MessageHandler(filters.Regex("^👤 ACCOUNT$"), account))
    application.add_handler(MessageHandler(filters.Regex("^📞 CONTACT ADMIN$"), contact_admin))

    # Start the bot
    application.run_polling()

if __name__ == "__main__":
    main()
