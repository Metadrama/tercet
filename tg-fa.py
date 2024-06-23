import asyncio
import subprocess
import os
from fastapi import FastAPI
from pydantic import BaseModel
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import uvicorn

# Replace with your Telegram Bot Token
TOKEN = "7469057741:AAGdNzQYuCRUw_AIb_60VSTE_QZ9KM4Ygzs"

# Set the path to the llama.cpp llama-cli executable
LLAMA_CPP_PATH = os.path.expanduser("~/llama.cpp/llama-cli")

app = FastAPI()

class Query(BaseModel):
    text: str

CUSTOM_INSTRUCTIONS = """My name is Wan Aminnur Rasheed Bin Wan Zainol, commonly called Amin or Mino. I am 25 years old, a student at UniKL MIIT in Kuala Lumpur, studying software engineering. I'm in my second year, approaching the third year of my bachelor's degree. Financial constraints are a significant concern, making earning money a top priority. I often analyze tiny details and create multi-step reasoning to solve problems efficiently and find ways to earn income. I use a Lenovo B41-80 laptop with an i5 6200u processor, AMD R5 M330, running custom Windows 11, and I work with Android Studio, Visual Studio Code, and Python. I also have a Samsung Galaxy S10+ with a custom OneUI 6.0 port, SU access with custom Magisk called Kitsune Mask.

I prefer concise, actionable responses with a focus on practical advice, especially related to financial opportunities. Critical thinking and multi-step problem-solving are important to me, so explanations that align with this approach are valuable. I also enjoy a bit of humor and wordplay in our interactions."""

@app.post("/generate")
async def generate(query: Query):
    prompt = f"{CUSTOM_INSTRUCTIONS}\n\nUser: {query.text}\nAssistant:"
    try:
        result = subprocess.run(
            [LLAMA_CPP_PATH, "-m", "dolphin-2.7-mixtral-8x7b.Q5_K_M.gguf", "-p", prompt, "-n", "512", "--temp", "0.7", "--top-p", "0.95"],
            capture_output=True,
            text=True,
            check=True
        )
        return {"response": result.stdout.split("Assistant:", 1)[-1].strip()}
    except subprocess.CalledProcessError as e:
        error_message = f"Error running llama-cli: {e}\n"
        error_message += f"Stdout: {e.stdout}\n"
        error_message += f"Stderr: {e.stderr}\n"
        return {"error": error_message}
    except FileNotFoundError:
        return {"error": f"llama-cli executable not found at {LLAMA_CPP_PATH}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

async def start(update: Update, context):
    await update.message.reply_text("Hello, Amin! I'm your AI assistant. How can I help you today?")

async def handle_message(update: Update, context):
    user_message = update.message.text
    query = Query(text=user_message)
    response = await generate(query)
    if "error" in response:
        await update.message.reply_text(f"An error occurred: {response['error']}")
    else:
        await update.message.reply_text(response["response"])

async def run_telegram_bot():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    await application.initialize()
    await application.start()
    await application.updater.start_polling()

async def run_fastapi():
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, loop="asyncio")
    server = uvicorn.Server(config)
    await server.serve()

async def main():
    await asyncio.gather(run_telegram_bot(), run_fastapi())

if __name__ == "__main__":
    asyncio.run(main())