import os
import threading
import uvicorn
from tgbot.bot import run_bot


def start_api():
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("compass.main:app", host="0.0.0.0", port=port)


if __name__ == "__main__":
    # FastAPI in a background thread
    api_thread = threading.Thread(target=start_api, daemon=True)
    api_thread.start()

    # Telegram bot in main thread (blocking — keeps process alive)
    run_bot()
