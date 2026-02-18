import asyncio
import io
import json
import os
import random
import textwrap
from datetime import date, time, datetime, timezone, timedelta

from PIL import Image, ImageDraw, ImageFont
from telegram import (
    BotCommand,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "user_data.json")

# --- quotes ---

QUOTES_NIETZSCHE = [
    ("\u0422\u0435, \u0449\u043e \u043d\u0430\u0441 \u043d\u0435 \u0432\u0431\u0438\u0432\u0430\u0454, \u0440\u043e\u0431\u0438\u0442\u044c \u043d\u0430\u0441 \u0441\u0438\u043b\u044c\u043d\u0456\u0448\u0438\u043c\u0438", "\u0424\u0440\u0456\u0434\u0440\u0456\u0445 \u041d\u0456\u0446\u0448\u0435"),
    ("\u0411\u0435\u0437 \u043c\u0443\u0437\u0438\u043a\u0438 \u0436\u0438\u0442\u0442\u044f \u0431\u0443\u043b\u043e \u0431 \u043f\u043e\u043c\u0438\u043b\u043a\u043e\u044e", "\u0424\u0440\u0456\u0434\u0440\u0456\u0445 \u041d\u0456\u0446\u0448\u0435"),
    ("\u0421\u0442\u0430\u043d\u044c \u0442\u0438\u043c, \u0445\u0442\u043e \u0442\u0438 \u0454", "\u0424\u0440\u0456\u0434\u0440\u0456\u0445 \u041d\u0456\u0446\u0448\u0435"),
    ("\u0411\u043e\u0433 \u043f\u043e\u043c\u0435\u0440, \u0456 \u043c\u0438 \u0439\u043e\u0433\u043e \u0432\u0431\u0438\u043b\u0438", "\u0424\u0440\u0456\u0434\u0440\u0456\u0445 \u041d\u0456\u0446\u0448\u0435"),
    ("\u0425\u0442\u043e \u043c\u0430\u0454 \u041d\u0430\u0432\u0456\u0449\u043e \u0436\u0438\u0442\u0438, \u043c\u043e\u0436\u0435 \u0432\u0438\u0442\u0440\u0438\u043c\u0430\u0442\u0438 \u043c\u0430\u0439\u0436\u0435 \u0431\u0443\u0434\u044c-\u044f\u043a\u0435 \u042f\u043a", "\u0424\u0440\u0456\u0434\u0440\u0456\u0445 \u041d\u0456\u0446\u0448\u0435"),
    (
        "\u0422\u043e\u0439, \u0445\u0442\u043e \u0431\u043e\u0440\u0435\u0442\u044c\u0441\u044f \u0437 \u0447\u0443\u0434\u043e\u0432\u0438\u0441\u044c\u043a\u0430\u043c\u0438, \u043c\u0430\u0454 \u0441\u0442\u0435\u0436\u0438\u0442\u0438, "
        "\u0449\u043e\u0431 \u0441\u0430\u043c\u043e\u043c\u0443 \u043d\u0435 \u0441\u0442\u0430\u0442\u0438 \u0447\u0443\u0434\u043e\u0432\u0438\u0441\u044c\u043a\u043e\u043c",
        "\u0424\u0440\u0456\u0434\u0440\u0456\u0445 \u041d\u0456\u0446\u0448\u0435",
    ),
    (
        "\u0412\u0441\u0435, \u0449\u043e \u0440\u043e\u0431\u0438\u0442\u044c\u0441\u044f \u0437 \u043b\u044e\u0431\u043e\u0432\u0456, \u043f\u0435\u0440\u0435\u0431\u0443\u0432\u0430\u0454 \u043f\u043e \u0442\u043e\u0439 \u0431\u0456\u043a \u0434\u043e\u0431\u0440\u0430 \u0456 \u0437\u043b\u0430",
        "\u0424\u0440\u0456\u0434\u0440\u0456\u0445 \u041d\u0456\u0446\u0448\u0435",
    ),
    ("\u0414\u0443\u043c\u043a\u0438 \u043f\u0440\u0438\u0445\u043e\u0434\u044f\u0442\u044c, \u043a\u043e\u043b\u0438 \u0432\u043e\u043d\u0438 \u0445\u043e\u0447\u0443\u0442\u044c, \u0430 \u043d\u0435 \u043a\u043e\u043b\u0438 \u0445\u043e\u0447\u0443 \u044f", "\u0424\u0440\u0456\u0434\u0440\u0456\u0445 \u041d\u0456\u0446\u0448\u0435"),
    ("\u0406\u0441\u0442\u0438\u043d\u0430 \u043f\u043e\u0442\u0432\u043e\u0440\u043d\u0430", "\u0424\u0440\u0456\u0434\u0440\u0456\u0445 \u041d\u0456\u0446\u0448\u0435"),
    (
        "\u041b\u044e\u0434\u0438\u043d\u0430 \u2014 \u0446\u0435 \u043a\u0430\u043d\u0430\u0442, \u043d\u0430\u0442\u044f\u0433\u043d\u0443\u0442\u0438\u0439 \u043c\u0456\u0436 \u0442\u0432\u0430\u0440\u0438\u043d\u043e\u044e \u0456 \u043d\u0430\u0434\u043b\u044e\u0434\u0438\u043d\u043e\u044e",
        "\u0424\u0440\u0456\u0434\u0440\u0456\u0445 \u041d\u0456\u0446\u0448\u0435",
    ),
    ("\u041d\u0430 \u0441\u0430\u043c\u043e\u0442\u0456 \u0432\u0438\u0440\u043e\u0441\u0442\u0430\u0454 \u0442\u0435, \u0449\u043e \u043a\u043e\u0436\u0435\u043d \u0443 \u0441\u043e\u0431\u0456 \u043d\u043e\u0441\u0438\u0442\u044c", "\u0424\u0440\u0456\u0434\u0440\u0456\u0445 \u041d\u0456\u0446\u0448\u0435"),
    ("\u041d\u0435\u043c\u0430\u0454 \u0444\u0430\u043a\u0442\u0456\u0432, \u0454 \u043b\u0438\u0448\u0435 \u0456\u043d\u0442\u0435\u0440\u043f\u0440\u0435\u0442\u0430\u0446\u0456\u0457", "\u0424\u0440\u0456\u0434\u0440\u0456\u0445 \u041d\u0456\u0446\u0448\u0435"),
    (
        "\u0429\u043e \u0430\u0431\u0441\u0442\u0440\u0430\u043a\u0442\u043d\u0456\u0448\u0430 \u0456\u0441\u0442\u0438\u043d\u0430, \u0442\u043e \u043f\u0440\u0438\u0432\u0430\u0431\u043b\u0438\u0432\u0456\u0448\u0430 \u0432\u043e\u043d\u0430 \u0434\u043b\u044f \u0440\u043e\u0437\u0443\u043c\u0443",
        "\u0424\u0440\u0456\u0434\u0440\u0456\u0445 \u041d\u0456\u0446\u0448\u0435",
    ),
    (
        "\u042f \u043b\u044e\u0431\u043b\u044e \u0442\u0438\u0445, \u0445\u0442\u043e \u043d\u0435 \u0437\u043d\u0430\u0454, \u044f\u043a \u0436\u0438\u0442\u0438 \u0456\u043d\u0430\u043a\u0448\u0435, \u043d\u0456\u0436 \u0433\u0438\u043d\u0443\u0447\u0438",
        "\u0424\u0440\u0456\u0434\u0440\u0456\u0445 \u041d\u0456\u0446\u0448\u0435",
    ),
    ("\u0423 \u043a\u043e\u0433\u043e \u043d\u0435\u043c\u0430\u0454 \u0434\u0432\u043e\u0445 \u0442\u0440\u0435\u0442\u0438\u043d \u0434\u043d\u044f \u0434\u043b\u044f \u0441\u0435\u0431\u0435, \u0442\u043e\u0439 \u0440\u0430\u0431", "\u0424\u0440\u0456\u0434\u0440\u0456\u0445 \u041d\u0456\u0446\u0448\u0435"),
]

QUOTES_SCHOPENHAUER = [
    ("\u0416\u0438\u0442\u0442\u044f \u043f\u043e\u0434\u0456\u0431\u043d\u0435 \u0434\u043e \u043c\u0430\u044f\u0442\u043d\u0438\u043a\u0430, \u0449\u043e \u0445\u0438\u0442\u0430\u0454\u0442\u044c\u0441\u044f \u043c\u0456\u0436 \u0441\u0442\u0440\u0430\u0436\u0434\u0430\u043d\u043d\u044f\u043c \u0456 \u043d\u0443\u0434\u044c\u0433\u043e\u044e", "\u0410\u0440\u0442\u0443\u0440 \u0428\u043e\u043f\u0435\u043d\u0433\u0430\u0443\u0435\u0440"),
    (
        "\u0422\u0430\u043b\u0430\u043d\u0442 \u0432\u043b\u0443\u0447\u0430\u0454 \u0432 \u0446\u0456\u043b\u044c, \u0443 \u044f\u043a\u0443 \u043d\u0456\u0445\u0442\u043e \u043d\u0435 \u043c\u043e\u0436\u0435 \u0432\u043b\u0443\u0447\u0438\u0442\u0438; "
        "\u0433\u0435\u043d\u0456\u0439 \u0432\u043b\u0443\u0447\u0430\u0454 \u0432 \u0446\u0456\u043b\u044c, \u044f\u043a\u0443 \u043d\u0456\u0445\u0442\u043e \u043d\u0435 \u0431\u0430\u0447\u0438\u0442\u044c",
        "\u0410\u0440\u0442\u0443\u0440 \u0428\u043e\u043f\u0435\u043d\u0433\u0430\u0443\u0435\u0440",
    ),
    ("\u041a\u043e\u0436\u0435\u043d \u043f\u0440\u0438\u0439\u043c\u0430\u0454 \u043c\u0435\u0436\u0443 \u0441\u0432\u043e\u0433\u043e \u043a\u0440\u0443\u0433\u043e\u0437\u043e\u0440\u0443 \u0437\u0430 \u043c\u0435\u0436\u0443 \u0441\u0432\u0456\u0442\u0443", "\u0410\u0440\u0442\u0443\u0440 \u0428\u043e\u043f\u0435\u043d\u0433\u0430\u0443\u0435\u0440"),
    ("\u0417\u0434\u043e\u0440\u043e\u0432\u0438\u0439 \u0436\u0435\u0431\u0440\u0430\u043a \u0449\u0430\u0441\u043b\u0438\u0432\u0456\u0448\u0438\u0439 \u0437\u0430 \u0445\u0432\u043e\u0440\u043e\u0433\u043e \u043a\u043e\u0440\u043e\u043b\u044f", "\u0410\u0440\u0442\u0443\u0440 \u0428\u043e\u043f\u0435\u043d\u0433\u0430\u0443\u0435\u0440"),
    ("\u0421\u0442\u0430\u043d \u0449\u0430\u0441\u0442\u044f \u2014 \u0446\u0435 \u0441\u0442\u0430\u043d \u0432\u0456\u0434\u0441\u0443\u0442\u043d\u043e\u0441\u0442\u0456 \u0441\u0442\u0440\u0430\u0436\u0434\u0430\u043d\u043d\u044f", "\u0410\u0440\u0442\u0443\u0440 \u0428\u043e\u043f\u0435\u043d\u0433\u0430\u0443\u0435\u0440"),
    (
        "\u0421\u0430\u043c\u043e\u0442\u043d\u0456\u0441\u0442\u044c \u0434\u0430\u0454 \u0456\u043d\u0442\u0435\u043b\u0435\u043a\u0442\u0443\u0430\u043b\u044c\u043d\u0456\u0439 \u043b\u044e\u0434\u0438\u043d\u0456 \u043f\u043e\u0434\u0432\u0456\u0439\u043d\u0443 \u043f\u0435\u0440\u0435\u0432\u0430\u0433\u0443: "
        "\u0431\u0443\u0442\u0438 \u0437 \u0441\u0430\u043c\u0438\u043c \u0441\u043e\u0431\u043e\u044e \u0456 \u043d\u0435 \u0431\u0443\u0442\u0438 \u0437 \u0456\u043d\u0448\u0438\u043c\u0438",
        "\u0410\u0440\u0442\u0443\u0440 \u0428\u043e\u043f\u0435\u043d\u0433\u0430\u0443\u0435\u0440",
    ),
]

QUOTES_KANT = [
    ("\u0422\u043e\u0439, \u0445\u0442\u043e \u0436\u043e\u0440\u0441\u0442\u043e\u043a\u0438\u0439 \u0434\u043e \u0442\u0432\u0430\u0440\u0438\u043d, \u0441\u0442\u0430\u0454 \u0447\u0435\u0440\u0441\u0442\u0432\u0438\u043c \u0456 \u0432 \u0441\u0442\u043e\u0441\u0443\u043d\u043a\u0430\u0445 \u0437 \u043b\u044e\u0434\u044c\u043c\u0438", "\u0406\u043c\u043c\u0430\u043d\u0443\u0457\u043b \u041a\u0430\u043d\u0442"),
    ("\u0417 \u043a\u0440\u0438\u0432\u043e\u0433\u043e \u0434\u0435\u0440\u0435\u0432\u0430 \u043b\u044e\u0434\u0441\u0442\u0432\u0430 \u043d\u0435 \u043c\u043e\u0436\u043d\u0430 \u0437\u0440\u043e\u0431\u0438\u0442\u0438 \u043d\u0456\u0447\u043e\u0433\u043e \u043f\u0440\u044f\u043c\u043e\u0433\u043e", "\u0406\u043c\u043c\u0430\u043d\u0443\u0457\u043b \u041a\u0430\u043d\u0442"),
    ("\u0414\u043e\u0441\u0432\u0456\u0434 \u0431\u0435\u0437 \u0442\u0435\u043e\u0440\u0456\u0457 \u0441\u043b\u0456\u043f\u0438\u0439, \u0430 \u0442\u0435\u043e\u0440\u0456\u044f \u0431\u0435\u0437 \u0434\u043e\u0441\u0432\u0456\u0434\u0443 \u2014 \u043b\u0438\u0448\u0435 \u0456\u043d\u0442\u0435\u043b\u0435\u043a\u0442\u0443\u0430\u043b\u044c\u043d\u0430 \u0433\u0440\u0430", "\u0406\u043c\u043c\u0430\u043d\u0443\u0457\u043b \u041a\u0430\u043d\u0442"),
]

QUOTES_SENECA = [
    ("\u041c\u0438 \u0441\u0442\u0440\u0430\u0436\u0434\u0430\u0454\u043c\u043e \u0447\u0430\u0441\u0442\u0456\u0448\u0435 \u0432 \u0443\u044f\u0432\u0456, \u043d\u0456\u0436 \u0443 \u0440\u0435\u0430\u043b\u044c\u043d\u043e\u0441\u0442\u0456", "\u0421\u0435\u043d\u0435\u043a\u0430"),
    ("\u0423\u0434\u0430\u0447\u0430 \u2014 \u0446\u0435 \u043a\u043e\u043b\u0438 \u043f\u0456\u0434\u0433\u043e\u0442\u043e\u0432\u043a\u0430 \u0437\u0443\u0441\u0442\u0440\u0456\u0447\u0430\u0454\u0442\u044c\u0441\u044f \u0437 \u043c\u043e\u0436\u043b\u0438\u0432\u0456\u0441\u0442\u044e", "\u0421\u0435\u043d\u0435\u043a\u0430"),
    ("\u0412\u0441\u0435 \u043c\u0430\u0439\u0431\u0443\u0442\u043d\u0454 \u043b\u0435\u0436\u0438\u0442\u044c \u0443 \u043d\u0435\u0432\u0456\u0434\u043e\u043c\u043e\u0441\u0442\u0456 \u2014 \u0436\u0438\u0432\u0438 \u0437\u0430\u0440\u0430\u0437", "\u0421\u0435\u043d\u0435\u043a\u0430"),
]

QUOTES_AURELIUS = [
    ("\u0422\u0438 \u0432\u043b\u0430\u0434\u043d\u0438\u0439 \u043d\u0430\u0434 \u0441\u0432\u043e\u0457\u043c \u0440\u043e\u0437\u0443\u043c\u043e\u043c, \u0430 \u043d\u0435 \u043d\u0430\u0434 \u0437\u043e\u0432\u043d\u0456\u0448\u043d\u0456\u043c\u0438 \u043f\u043e\u0434\u0456\u044f\u043c\u0438. \u0417\u0440\u043e\u0437\u0443\u043c\u0456\u0439 \u0446\u0435 \u2014 \u0456 \u0437\u043d\u0430\u0439\u0434\u0435\u0448 \u0441\u0438\u043b\u0443", "\u041c\u0430\u0440\u043a \u0410\u0432\u0440\u0435\u043b\u0456\u0439"),
    ("\u0429\u0430\u0441\u0442\u044f \u0442\u0432\u043e\u0433\u043e \u0436\u0438\u0442\u0442\u044f \u0437\u0430\u043b\u0435\u0436\u0438\u0442\u044c \u0432\u0456\u0434 \u044f\u043a\u043e\u0441\u0442\u0456 \u0442\u0432\u043e\u0457\u0445 \u0434\u0443\u043c\u043e\u043a", "\u041c\u0430\u0440\u043a \u0410\u0432\u0440\u0435\u043b\u0456\u0439"),
    ("\u041d\u0435 \u0432\u0438\u0442\u0440\u0430\u0447\u0430\u0439 \u0447\u0430\u0441 \u043d\u0430 \u0441\u0443\u043f\u0435\u0440\u0435\u0447\u043a\u0438 \u043f\u0440\u043e \u0442\u0435, \u044f\u043a\u0438\u043c \u043c\u0430\u0454 \u0431\u0443\u0442\u0438 \u0445\u043e\u0440\u043e\u0448\u0438\u0439 \u0447\u043e\u043b\u043e\u0432\u0456\u043a. \u0411\u0443\u0434\u044c \u043d\u0438\u043c", "\u041c\u0430\u0440\u043a \u0410\u0432\u0440\u0435\u043b\u0456\u0439"),
    ("\u0414\u0443\u0448\u0430 \u0437\u0430\u0431\u0430\u0440\u0432\u043b\u044e\u0454\u0442\u044c\u0441\u044f \u0443 \u043a\u043e\u043b\u0456\u0440 \u0441\u0432\u043e\u0457\u0445 \u0434\u0443\u043c\u043e\u043a", "\u041c\u0430\u0440\u043a \u0410\u0432\u0440\u0435\u043b\u0456\u0439"),
]

ALL_QUOTES = QUOTES_NIETZSCHE + QUOTES_SCHOPENHAUER + QUOTES_KANT + QUOTES_SENECA + QUOTES_AURELIUS

CATEGORY_LABELS = {
    "nietzsche": "\u041d\u0456\u0446\u0448\u0435",
    "schopenhauer": "\u0428\u043e\u043f\u0435\u043d\u0433\u0430\u0443\u0435\u0440",
    "kant": "\u041a\u0430\u043d\u0442",
    "seneca": "\u0421\u0435\u043d\u0435\u043a\u0430",
    "aurelius": "\u041c\u0430\u0440\u043a \u0410\u0432\u0440\u0435\u043b\u0456\u0439",
    "random": "\u0412\u0438\u043f\u0430\u0434\u043a\u043e\u0432\u0430",
}

POOLS = {
    "nietzsche": QUOTES_NIETZSCHE,
    "schopenhauer": QUOTES_SCHOPENHAUER,
    "kant": QUOTES_KANT,
    "seneca": QUOTES_SENECA,
    "aurelius": QUOTES_AURELIUS,
}

DAILY_HOURS = [7, 8, 9, 10, 12, 14, 18, 20, 22]


# --- persistence ---

def load_data() -> dict:
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_data(data: dict) -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_user(data: dict, user_id: int) -> dict:
    uid = str(user_id)
    if uid not in data:
        data[uid] = {
            "daily_date": None,
            "daily_quote": None,
            "auto_enabled": False,
            "auto_hour": 9,
        }
    user = data[uid]
    user.setdefault("auto_enabled", False)
    user.setdefault("auto_hour", 9)
    return user


# --- image generation ---

def _find_font(bold: bool = False) -> str:
    candidates = (
        [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "C:/Windows/Fonts/arialbd.ttf",
        ]
        if bold
        else [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "C:/Windows/Fonts/arial.ttf",
        ]
    )
    for path in candidates:
        if os.path.exists(path):
            return path
    return ""


def generate_quote_image(text: str, author: str) -> bytes:
    width, height = 800, 600
    img = Image.new("RGB", (width, height), color=(30, 30, 40))
    draw = ImageDraw.Draw(img)

    font_path = _find_font(bold=False)
    font_bold_path = _find_font(bold=True)

    if font_path:
        font_quote = ImageFont.truetype(font_path, 28)
    else:
        font_quote = ImageFont.load_default()

    if font_bold_path:
        font_author = ImageFont.truetype(font_bold_path, 22)
    else:
        font_author = ImageFont.load_default()

    wrapped = textwrap.fill(f"\u201c{text}\u201d", width=38)
    author_line = f"\u2014 {author}"

    q_bbox = draw.multiline_textbbox((0, 0), wrapped, font=font_quote)
    q_w = q_bbox[2] - q_bbox[0]
    q_h = q_bbox[3] - q_bbox[1]

    a_bbox = draw.textbbox((0, 0), author_line, font=font_author)
    a_w = a_bbox[2] - a_bbox[0]

    total_h = q_h + 40 + (a_bbox[3] - a_bbox[1])
    y_start = (height - total_h) // 2

    draw.line([(100, y_start - 30), (width - 100, y_start - 30)], fill=(180, 160, 120), width=2)

    draw.multiline_text(
        ((width - q_w) // 2, y_start),
        wrapped,
        font=font_quote,
        fill=(235, 235, 235),
        align="center",
    )

    draw.text(
        ((width - a_w) // 2, y_start + q_h + 40),
        author_line,
        font=font_author,
        fill=(180, 160, 120),
    )

    draw.line(
        [(100, y_start + q_h + 80 + 20), (width - 100, y_start + q_h + 80 + 20)],
        fill=(180, 160, 120),
        width=2,
    )

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf.getvalue()


# --- keyboards ---

def philosopher_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("\u041a\u0430\u043d\u0442", callback_data="cat_kant"),
            InlineKeyboardButton("\u0421\u0435\u043d\u0435\u043a\u0430", callback_data="cat_seneca"),
            InlineKeyboardButton("\u041c\u0430\u0440\u043a \u0410\u0432\u0440\u0435\u043b\u0456\u0439", callback_data="cat_aurelius"),
        ],
        [
            InlineKeyboardButton("\ud83c\udfb2 \u0412\u0438\u043f\u0430\u0434\u043a\u043e\u0432\u0430", callback_data="cat_random"),
        ],
    ])


def quote_keyboard(quote_index: int, category: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("\U0001f4e4 \u041f\u043e\u0434\u0456\u043b\u0438\u0442\u0438\u0441\u044c", callback_data=f"share_{quote_index}"),
            InlineKeyboardButton("\u0429\u0435 \u0446\u0438\u0442\u0430\u0442\u0443!", callback_data=f"next_{category}"),
        ],
    ])


def auto_settings_keyboard(user: dict) -> InlineKeyboardMarkup:
    enabled = user.get("auto_enabled", False)
    hour = user.get("auto_hour", 9)
    status_text = "\u2705 \u0423\u0432\u0456\u043c\u043a." if enabled else "\u274c \u0412\u0438\u043c\u043a."
    toggle_data = "auto_off" if enabled else "auto_on"

    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"\u0429\u043e\u0434\u0435\u043d\u043d\u0430 \u0446\u0438\u0442\u0430\u0442\u0430: {status_text}", callback_data=toggle_data)],
        [
            InlineKeyboardButton("\u25c0", callback_data="hour_dec"),
            InlineKeyboardButton(f"\u0427\u0430\u0441: {hour:02d}:00", callback_data="hour_noop"),
            InlineKeyboardButton("\u25b6", callback_data="hour_inc"),
        ],
    ])


# --- helpers ---

def format_quote(text: str, author: str) -> str:
    return f'\u201c{text}\u201d\n\n\u2014 {author}'


def pick_quote(category: str, context: ContextTypes.DEFAULT_TYPE | None = None) -> tuple[int, str, str]:
    last_idx = None
    if context and context.user_data:
        last_idx = context.user_data.get("last_quote_idx")

    pool = POOLS.get(category, ALL_QUOTES)
    while True:
        q = random.choice(pool)
        idx = ALL_QUOTES.index(q)
        if idx != last_idx or len(pool) == 1:
            break

    if context is not None:
        context.user_data["last_quote_idx"] = idx
    return idx, q[0], q[1]


# --- scheduled daily quote ---

async def send_scheduled_quote(context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = context.job.chat_id
    idx, text, author = pick_quote("random")
    await context.bot.send_message(
        chat_id=chat_id,
        text=f"\u2728 \u0426\u0438\u0442\u0430\u0442\u0430 \u0434\u043d\u044f:\n\n{format_quote(text, author)}",
        reply_markup=quote_keyboard(idx, "random"),
    )


def schedule_user_job(app: Application, chat_id: int, hour: int) -> None:
    job_name = f"daily_{chat_id}"
    # remove old job if exists
    for job in app.job_queue.get_jobs_by_name(job_name):
        job.schedule_removal()
    # UTC time for the given hour (assuming user is UTC+2 Kyiv)
    utc_hour = (hour - 2) % 24
    app.job_queue.run_daily(
        send_scheduled_quote,
        time=time(hour=utc_hour, minute=0, tzinfo=timezone.utc),
        chat_id=chat_id,
        name=job_name,
    )


def remove_user_job(app: Application, chat_id: int) -> None:
    job_name = f"daily_{chat_id}"
    for job in app.job_queue.get_jobs_by_name(job_name):
        job.schedule_removal()


# --- handlers ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "\u041f\u0440\u0438\u0432\u0456\u0442! \u042f \u0431\u043e\u0442 \u0437 \u0444\u0456\u043b\u043e\u0441\u043e\u0444\u0441\u044c\u043a\u0438\u043c\u0438 \u0446\u0438\u0442\u0430\u0442\u0430\u043c\u0438.\n\n"
        "\ud83d\udcdc /quote \u2014 \u043e\u0442\u0440\u0438\u043c\u0430\u0442\u0438 \u0446\u0438\u0442\u0430\u0442\u0443\n"
        "\ud83d\udcc5 /daily \u2014 \u0446\u0438\u0442\u0430\u0442\u0430 \u0434\u043d\u044f\n"
        "\u2699\ufe0f /settings \u2014 \u0449\u043e\u0434\u0435\u043d\u043d\u0430 \u0440\u043e\u0437\u0441\u0438\u043b\u043a\u0430",
    )


async def quote_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "\u041e\u0431\u0435\u0440\u0438 \u0444\u0456\u043b\u043e\u0441\u043e\u0444\u0430:",
        reply_markup=philosopher_keyboard(),
    )


async def category_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    cat = query.data.replace("cat_", "")
    idx, text, author = pick_quote(cat, context)
    await query.message.reply_text(
        format_quote(text, author), reply_markup=quote_keyboard(idx, cat)
    )


async def daily(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    data = load_data()
    user = get_user(data, update.effective_user.id)
    today = date.today().isoformat()

    if user["daily_date"] == today and user["daily_quote"] is not None:
        idx = user["daily_quote"]
        text, author = ALL_QUOTES[idx]
        await update.message.reply_text(
            f"\u0422\u0432\u043e\u044f \u0446\u0438\u0442\u0430\u0442\u0430 \u043d\u0430 \u0441\u044c\u043e\u0433\u043e\u0434\u043d\u0456:\n\n{format_quote(text, author)}\n\n"
            "(\u041d\u0430\u0441\u0442\u0443\u043f\u043d\u0430 \u0431\u0443\u0434\u0435 \u0437\u0430\u0432\u0442\u0440\u0430!)",
            reply_markup=quote_keyboard(idx, "random"),
        )
        return

    idx = random.randrange(len(ALL_QUOTES))
    user["daily_date"] = today
    user["daily_quote"] = idx
    save_data(data)

    text, author = ALL_QUOTES[idx]
    await update.message.reply_text(
        f"\u0426\u0438\u0442\u0430\u0442\u0430 \u0434\u043d\u044f:\n\n{format_quote(text, author)}",
        reply_markup=quote_keyboard(idx, "random"),
    )


async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "\n" * 50 + "\u0427\u0430\u0442 \u043e\u0447\u0438\u0449\u0435\u043d\u043e!",
    )


async def settings_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    data = load_data()
    user = get_user(data, update.effective_user.id)
    save_data(data)
    await update.message.reply_text(
        "\u2699\ufe0f \u041d\u0430\u043b\u0430\u0448\u0442\u0443\u0432\u0430\u043d\u043d\u044f \u0449\u043e\u0434\u0435\u043d\u043d\u043e\u0457 \u0446\u0438\u0442\u0430\u0442\u0438:\n"
        "(\u0447\u0430\u0441 \u0437\u0430 \u043a\u0438\u0457\u0432\u0441\u044c\u043a\u0438\u043c \u0447\u0430\u0441\u043e\u043c)",
        reply_markup=auto_settings_keyboard(user),
    )


async def auto_toggle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = load_data()
    user = get_user(data, query.from_user.id)

    if query.data == "auto_on":
        user["auto_enabled"] = True
        schedule_user_job(context.application, query.message.chat_id, user["auto_hour"])
    else:
        user["auto_enabled"] = False
        remove_user_job(context.application, query.message.chat_id)

    save_data(data)
    await query.message.edit_reply_markup(reply_markup=auto_settings_keyboard(user))


async def hour_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == "hour_noop":
        return

    data = load_data()
    user = get_user(data, query.from_user.id)
    h = user.get("auto_hour", 9)

    if query.data == "hour_inc":
        h = (h + 1) % 24
    else:
        h = (h - 1) % 24

    user["auto_hour"] = h
    save_data(data)

    if user.get("auto_enabled"):
        schedule_user_job(context.application, query.message.chat_id, h)

    await query.message.edit_reply_markup(reply_markup=auto_settings_keyboard(user))


async def next_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    cat = query.data.replace("next_", "")
    idx, text, author = pick_quote(cat, context)
    await query.message.reply_text(
        format_quote(text, author), reply_markup=quote_keyboard(idx, cat)
    )


async def share_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    idx = int(query.data.replace("share_", ""))
    text, author = ALL_QUOTES[idx]
    img_bytes = generate_quote_image(text, author)
    await query.message.reply_photo(
        photo=img_bytes,
        caption=format_quote(text, author),
    )


async def post_init(application: Application) -> None:
    await application.bot.set_my_commands([
        BotCommand("start", "\u0417\u0430\u043f\u0443\u0441\u0442\u0438\u0442\u0438 \u0431\u043e\u0442\u0430"),
        BotCommand("quote", "\u041e\u0442\u0440\u0438\u043c\u0430\u0442\u0438 \u0446\u0438\u0442\u0430\u0442\u0443"),
        BotCommand("daily", "\u0426\u0438\u0442\u0430\u0442\u0430 \u0434\u043d\u044f"),
        BotCommand("settings", "\u041d\u0430\u043b\u0430\u0448\u0442\u0443\u0432\u0430\u043d\u043d\u044f"),
        BotCommand("clear", "\u041e\u0447\u0438\u0441\u0442\u0438\u0442\u0438 \u0447\u0430\u0442"),
    ])

    # restore scheduled jobs for users with auto_enabled
    data = load_data()
    for uid, udata in data.items():
        if udata.get("auto_enabled"):
            try:
                schedule_user_job(application, int(uid), udata.get("auto_hour", 9))
            except Exception:
                pass


def run_bot() -> None:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    app = Application.builder().token(TOKEN).post_init(post_init).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("clear", clear))
    app.add_handler(CommandHandler("quote", quote_cmd))
    app.add_handler(CommandHandler("daily", daily))
    app.add_handler(CommandHandler("settings", settings_cmd))

    app.add_handler(CallbackQueryHandler(category_callback, pattern=r"^cat_"))
    app.add_handler(CallbackQueryHandler(next_callback, pattern=r"^next_"))
    app.add_handler(CallbackQueryHandler(share_callback, pattern=r"^share_"))
    app.add_handler(CallbackQueryHandler(auto_toggle_callback, pattern=r"^auto_"))
    app.add_handler(CallbackQueryHandler(hour_callback, pattern=r"^hour_"))

    print("Telegram bot started...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    run_bot()
