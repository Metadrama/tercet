import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import aiohttp

# Replace with your Telegram Bot Token
TOKEN = "7469057741:AAGdNzQYuCRUw_AIb_60VSTE_QZ9KM4Ygzs"

async def start(update: Update, context):
    await update.message.reply_text("Hello! I'm your AI assistant. How can I help you today?")

async def handle_message(update: Update, context):
    user_message = update.message.text
    async with aiohttp.ClientSession() as session:
        async with session.post("http://localhost:8000/generate", json={"text": user_message}) as response:
            if response.status == 200:
                data = await response.json()
                ai_response = data["response"]
                await update.message.reply_text(ai_response)
            else:
                await update.message.reply_text("Sorry, I couldn't process your request.")

def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling()

if __name__ == "__main__":
    main()
