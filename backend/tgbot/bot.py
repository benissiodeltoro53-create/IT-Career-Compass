import asyncio
import io
import json
import os
import random
import textwrap
from datetime import date

from PIL import Image, ImageDraw, ImageFont
from telegram import (
    BotCommand,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    Update,
)
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "user_data.json")

QUOTES_NIETZSCHE = [
    ("What does not kill me makes me stronger", "Friedrich Nietzsche"),
    ("Without music, life would be a mistake", "Friedrich Nietzsche"),
    ("Become who you are", "Friedrich Nietzsche"),
    ("God is dead, and we have killed him", "Friedrich Nietzsche"),
    ("He who has a Why to live can bear almost any How", "Friedrich Nietzsche"),
    (
        "He who fights with monsters should see to it "
        "that he himself does not become a monster",
        "Friedrich Nietzsche",
    ),
    (
        "Everything done out of love takes place beyond good and evil",
        "Friedrich Nietzsche",
    ),
    ("Thoughts come when they want to, not when I want them to", "Friedrich Nietzsche"),
    ("Truth is ugly", "Friedrich Nietzsche"),
    (
        "Man is a rope stretched between the animal and the overman",
        "Friedrich Nietzsche",
    ),
    ("In solitude, what everyone carries within themselves grows", "Friedrich Nietzsche"),
    ("There are no facts, only interpretations", "Friedrich Nietzsche"),
    (
        "The more abstract the truth, the more appealing it is to the mind",
        "Friedrich Nietzsche",
    ),
    (
        "I love those who do not know how to live except by going under",
        "Friedrich Nietzsche",
    ),
    ("Anyone who does not have two-thirds of the day for himself is a slave", "Friedrich Nietzsche"),
]

QUOTES_SCHOPENHAUER = [
    (
        "Life swings like a pendulum between suffering and boredom",
        "Arthur Schopenhauer",
    ),
    (
        "Talent hits a target no one else can hit; "
        "genius hits a target no one else can see",
        "Arthur Schopenhauer",
    ),
    (
        "Every person takes the limits of their own field of vision for the limits of the world",
        "Arthur Schopenhauer",
    ),
    ("A healthy beggar is happier than a sick king", "Arthur Schopenhauer"),
    (
        "Happiness is the absence of suffering",
        "Arthur Schopenhauer",
    ),
    (
        "Solitude gives the intellectual person a double advantage: "
        "being with oneself and not being with others",
        "Arthur Schopenhauer",
    ),
]

QUOTES_KANT = [
    ("He who is cruel to animals becomes hard also in his dealings with men", "Immanuel Kant"),
    ("Out of the crooked timber of humanity, no straight thing was ever made", "Immanuel Kant"),
    ("Experience without theory is blind, but theory without experience is mere intellectual play", "Immanuel Kant"),
]

QUOTES_SENECA = [
    ("We suffer more often in imagination than in reality", "Seneca"),
    ("Luck is what happens when preparation meets opportunity", "Seneca"),
    ("The whole future lies in uncertainty — live immediately", "Seneca"),
]

QUOTES_AURELIUS = [
    ("You have power over your mind, not outside events. Realize this, and you will find strength", "Marcus Aurelius"),
    ("The happiness of your life depends upon the quality of your thoughts", "Marcus Aurelius"),
    ("Waste no more time arguing about what a good man should be. Be one", "Marcus Aurelius"),
    ("The soul becomes dyed with the color of its thoughts", "Marcus Aurelius"),
]

ALL_QUOTES = QUOTES_NIETZSCHE + QUOTES_SCHOPENHAUER + QUOTES_KANT + QUOTES_SENECA + QUOTES_AURELIUS

# Category button labels
BTN_NIETZSCHE = "Nietzsche"
BTN_SCHOPENHAUER = "Schopenhauer"
BTN_KANT = "Kant"
BTN_SENECA = "Seneca"
BTN_AURELIUS = "Aurelius"
BTN_RANDOM = "Random"

CATEGORY_MAP = {
    BTN_NIETZSCHE: "nietzsche",
    BTN_SCHOPENHAUER: "schopenhauer",
    BTN_KANT: "kant",
    BTN_SENECA: "seneca",
    BTN_AURELIUS: "aurelius",
    BTN_RANDOM: "random",
}


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
        data[uid] = {"daily_date": None, "daily_quote": None}
    return data[uid]


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

BOTTOM_KEYBOARD = ReplyKeyboardMarkup(
    [
        [KeyboardButton(BTN_NIETZSCHE), KeyboardButton(BTN_SCHOPENHAUER), KeyboardButton(BTN_KANT)],
        [KeyboardButton(BTN_SENECA), KeyboardButton(BTN_AURELIUS), KeyboardButton(BTN_RANDOM)],
    ],
    resize_keyboard=True,
)


def quote_keyboard(quote_index: int, category: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("\U0001f4e4 Share", callback_data=f"share_{quote_index}"),
            InlineKeyboardButton("Next quote!", callback_data=f"next_{category}"),
        ],
    ])


# --- helpers ---

_last_quote_idx: int | None = None


def format_quote(text: str, author: str) -> str:
    return f'\u201c{text}\u201d\n\n\u2014 {author}'


def pick_quote(category: str) -> tuple[int, str, str]:
    global _last_quote_idx
    pools = {
        "nietzsche": QUOTES_NIETZSCHE,
        "schopenhauer": QUOTES_SCHOPENHAUER,
        "kant": QUOTES_KANT,
        "seneca": QUOTES_SENECA,
        "aurelius": QUOTES_AURELIUS,
    }
    pool = pools.get(category, ALL_QUOTES)
    while True:
        q = random.choice(pool)
        idx = ALL_QUOTES.index(q)
        if idx != _last_quote_idx or len(pool) == 1:
            break
    _last_quote_idx = idx
    return idx, q[0], q[1]


# --- handlers ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Hello! I'm a bot with philosophical quotes by Nietzsche and Schopenhauer.\n\n"
        "Pick a category below or press /quote for a random quote.",
        reply_markup=BOTTOM_KEYBOARD,
    )


async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "\n" * 50 + "Chat cleared! Pick a category below.",
        reply_markup=BOTTOM_KEYBOARD,
    )


async def quote(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    idx, text, author = pick_quote("random")
    await update.message.reply_text(
        format_quote(text, author), reply_markup=quote_keyboard(idx, "random")
    )


async def daily(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    data = load_data()
    user = get_user(data, update.effective_user.id)
    today = date.today().isoformat()

    if user["daily_date"] == today and user["daily_quote"] is not None:
        idx = user["daily_quote"]
        text, author = ALL_QUOTES[idx]
        await update.message.reply_text(
            f"Your quote for today:\n\n{format_quote(text, author)}\n\n"
            "(Next one tomorrow!)",
            reply_markup=quote_keyboard(idx, "random"),
        )
        return

    idx = random.randrange(len(ALL_QUOTES))
    user["daily_date"] = today
    user["daily_quote"] = idx
    save_data(data)

    text, author = ALL_QUOTES[idx]
    await update.message.reply_text(
        f"Quote of the day:\n\n{format_quote(text, author)}",
        reply_markup=quote_keyboard(idx, "random"),
    )


async def category_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    cat = CATEGORY_MAP.get(update.message.text)
    if not cat:
        return
    idx, text, author = pick_quote(cat)
    await update.message.reply_text(
        format_quote(text, author), reply_markup=quote_keyboard(idx, cat)
    )


async def next_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    cat = query.data.replace("next_", "")
    idx, text, author = pick_quote(cat)
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


async def post_init(application) -> None:
    await application.bot.set_my_commands([
        BotCommand("start", "Start the bot"),
        BotCommand("clear", "Clear the chat"),
    ])


def run_bot() -> None:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    app = Application.builder().token(TOKEN).post_init(post_init).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("clear", clear))
    app.add_handler(CommandHandler("quote", quote))
    app.add_handler(CommandHandler("daily", daily))

    app.add_handler(MessageHandler(
        filters.TEXT & filters.Regex(f"^({BTN_NIETZSCHE}|{BTN_SCHOPENHAUER}|{BTN_KANT}|{BTN_SENECA}|{BTN_AURELIUS}|{BTN_RANDOM})$"),
        category_text,
    ))

    app.add_handler(CallbackQueryHandler(next_callback, pattern=r"^next_"))
    app.add_handler(CallbackQueryHandler(share_callback, pattern=r"^share_"))

    print("Telegram bot started...")
    app.run_polling()


if __name__ == "__main__":
    run_bot()
