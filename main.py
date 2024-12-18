from telegram import Update, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters,
    ContextTypes, ConversationHandler
)
from datetime import datetime

# Replace 'YOUR_BOT_TOKEN' with the bot token you got from BotFather
BOT_TOKEN = "7623760590:AAE7wdcjENu26s84Veb1RrNDwGF-w1hDz6M"

# Conversation states
WALLET_ADDRESS, AMOUNT = range(2)

# In-memory balance store (for demo purposes)
user_balances = {}

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome! Use the menu to interact with the bot.")

# Wallet command
async def wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    wallet_address = "5k8s9uWoCJ9Nzoz3tAyN8TbvLK3zNdLk8B1YZ8MT2oAp"  # Example wallet address
    await update.message.reply_text(f"Your wallet address: {wallet_address}")

# Balance command
async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)  # Convert user ID to string for consistency
    balance = user_balances.get(user_id, 100)  # Default balance = 100 USDT for new users
    await update.message.reply_text(f"Your current balance: {balance} USDT")

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
    user_id = str(update.effective_user.id)  # Convert user ID to string for consistency
    wallet = context.user_data.get("wallet_address")
    amount_text = update.message.text.strip()

    # Validate the amount
    if not amount_text.isdigit() or int(amount_text) <= 0:
        await update.message.reply_text("Invalid amount. Please enter a positive number.")
        return AMOUNT

    amount = int(amount_text)

    # Initialize balance if the user is new
    if user_id not in user_balances:
        user_balances[user_id] = 100  # Default balance for new users

    # Check if the user has sufficient balance
    if user_balances[user_id] < amount:
        await update.message.reply_text(
            f"Insufficient balance. Your current balance is {user_balances[user_id]} USDT."
        )
        return ConversationHandler.END

    # Deduct the balance and confirm withdrawal
    user_balances[user_id] -= amount
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    await update.message.reply_text(
        f"Withdrawal successful!\n\n"
        f"Amount: {amount} USDT\n"
        f"Wallet Address: {wallet}\n"
        f"Transaction Time: {timestamp}\n"
        f"Remaining Balance: {user_balances[user_id]} USDT"
    )
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

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()