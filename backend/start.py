import os
import time
import threading
import urllib.request
import uvicorn
from tgbot.bot import run_bot


def start_api():
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("compass.main:app", host="0.0.0.0", port=port)


def self_ping():
    url = os.environ.get("RENDER_EXTERNAL_URL", "http://localhost:10000")
    print(f"Self-ping URL: {url}")
    while True:
        time.sleep(600)  # каждые 10 минут
        try:
            urllib.request.urlopen(url, timeout=10)
            print("Self-ping OK")
        except Exception as e:
            print(f"Self-ping FAILED: {e}")


if __name__ == "__main__":
    # FastAPI in a background thread
    api_thread = threading.Thread(target=start_api, daemon=True)
    api_thread.start()

    # Self-ping to prevent Render from sleeping
    ping_thread = threading.Thread(target=self_ping, daemon=True)
    ping_thread.start()

    # Telegram bot in main thread (blocking — keeps process alive)
    run_bot()
