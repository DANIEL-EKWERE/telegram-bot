from telegram import Update, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters,
    ContextTypes, ConversationHandler
)
#7142580406
# Replace 'YOUR_BOT_TOKEN' with the bot token you got from BotFather
BOT_TOKEN = "7623760590:AAE7wdcjENu26s84Veb1RrNDwGF-w1hDz6M"

async def get_chat_id(update:Update, context:ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await update.message.reply_text(f"your chat id is: {chat_id}")
    print(f"your chat id is: {chat_id}")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", get_chat_id))

    print("send start to the bot to get your start id")
    app.run_polling()

if __name__ == "__main__":
    main()