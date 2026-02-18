import threading
import uvicorn
from tgbot.bot import run_bot


def start_api():
    uvicorn.run("compass.main:app", host="0.0.0.0", port=10000)


if __name__ == "__main__":
    # FastAPI in a background thread
    api_thread = threading.Thread(target=start_api, daemon=True)
    api_thread.start()

    # Telegram bot in main thread (blocking — keeps process alive)
    run_bot()
