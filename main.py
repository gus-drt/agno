import asyncio
from telegram_bot import run_bot

if __name__ == "__main__":
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        print("Bot encerrado pelo usuário.")
