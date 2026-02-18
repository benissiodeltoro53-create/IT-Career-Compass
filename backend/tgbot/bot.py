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
    ("Те, що нас не вбиває, робить нас сильнішими", "Фрідріх Ніцше"),
    ("Без музики життя було б помилкою", "Фрідріх Ніцше"),
    ("Стань тим, хто ти є", "Фрідріх Ніцше"),
    ("Бог помер, і ми його вбили", "Фрідріх Ніцше"),
    ("Хто має Навіщо жити, може витримати майже будь-яке Як", "Фрідріх Ніцше"),
    (
        "Той, хто бореться з чудовиськами, має стежити, "
        "щоб самому не стати чудовиськом",
        "Фрідріх Ніцше",
    ),
    (
        "Все, що робиться з любові, перебуває по той бік добра і зла",
        "Фрідріх Ніцше",
    ),
    ("Думки приходять, коли вони хочуть, а не коли хочу я", "Фрідріх Ніцше"),
    ("Істина потворна", "Фрідріх Ніцше"),
    (
        "Людина — це канат, натягнутий між твариною і надлюдиною",
        "Фрідріх Ніцше",
    ),
    ("На самоті виростає те, що кожен у собі носить", "Фрідріх Ніцше"),
    ("Немає фактів, є лише інтерпретації", "Фрідріх Ніцше"),
    (
        "Що абстрактніша істина, то привабливіша вона для розуму",
        "Фрідріх Ніцше",
    ),
    (
        "Я люблю тих, хто не знає, як жити інакше, ніж гинучи",
        "Фрідріх Ніцше",
    ),
    ("У кого немає двох третин дня для себе, той раб", "Фрідріх Ніцше"),
]

QUOTES_SCHOPENHAUER = [
    (
        "Життя подібне до маятника, що хитається між стражданням і нудьгою",
        "Артур Шопенгауер",
    ),
    (
        "Талант влучає в ціль, у яку ніхто не може влучити; "
        "геній влучає в ціль, яку ніхто не бачить",
        "Артур Шопенгауер",
    ),
    (
        "Кожен приймає межу свого кругозору за межу світу",
        "Артур Шопенгауер",
    ),
    ("Здоровий жебрак щасливіший за хворого короля", "Артур Шопенгауер"),
    (
        "Стан щастя — це стан відсутності страждання",
        "Артур Шопенгауер",
    ),
    (
        "Самотність дає інтелектуальній людині подвійну перевагу: "
        "бути з самим собою і не бути з іншими",
        "Артур Шопенгауер",
    ),
]

ALL_QUOTES = QUOTES_NIETZSCHE + QUOTES_SCHOPENHAUER

# Category button labels
BTN_NIETZSCHE = "Ніцше"
BTN_SCHOPENHAUER = "Шопенгауер"
BTN_RANDOM = "Випадкова"

CATEGORY_MAP = {
    BTN_NIETZSCHE: "nietzsche",
    BTN_SCHOPENHAUER: "schopenhauer",
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

# Fixed bottom keyboard (ReplyKeyboard — always visible near input)
BOTTOM_KEYBOARD = ReplyKeyboardMarkup(
    [[KeyboardButton(BTN_NIETZSCHE), KeyboardButton(BTN_SCHOPENHAUER), KeyboardButton(BTN_RANDOM)]],
    resize_keyboard=True,
)


def quote_keyboard(quote_index: int, category: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("\U0001f4e4 Share", callback_data=f"share_{quote_index}"),
            InlineKeyboardButton("Ще цитату!", callback_data=f"next_{category}"),
        ],
    ])


# --- helpers ---

def format_quote(text: str, author: str) -> str:
    return f'\u201c{text}\u201d\n\n\u2014 {author}'


def pick_quote(category: str) -> tuple[int, str, str]:
    if category == "nietzsche":
        q = random.choice(QUOTES_NIETZSCHE)
    elif category == "schopenhauer":
        q = random.choice(QUOTES_SCHOPENHAUER)
    else:
        q = random.choice(ALL_QUOTES)
    idx = ALL_QUOTES.index(q)
    return idx, q[0], q[1]


# --- handlers ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Привіт! Я бот з філософськими цитатами Ніцше та Шопенгауера.\n\n"
        "Обери категорію внизу або натисни /quote для випадкової цитати.",
        reply_markup=BOTTOM_KEYBOARD,
    )


async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "\n" * 50 + "Чат очищено! Обери категорію внизу.",
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
            f"Твоя цитата на сьогодні:\n\n{format_quote(text, author)}\n\n"
            "(Наступна буде завтра!)",
            reply_markup=quote_keyboard(idx, "random"),
        )
        return

    idx = random.randrange(len(ALL_QUOTES))
    user["daily_date"] = today
    user["daily_quote"] = idx
    save_data(data)

    text, author = ALL_QUOTES[idx]
    await update.message.reply_text(
        f"Цитата дня:\n\n{format_quote(text, author)}",
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
        BotCommand("start", "Запустити бота"),
        BotCommand("clear", "Очистити чат"),
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
        filters.TEXT & filters.Regex(f"^({BTN_NIETZSCHE}|{BTN_SCHOPENHAUER}|{BTN_RANDOM})$"),
        category_text,
    ))

    app.add_handler(CallbackQueryHandler(next_callback, pattern=r"^next_"))
    app.add_handler(CallbackQueryHandler(share_callback, pattern=r"^share_"))

    print("Telegram bot started...")
    app.run_polling()


if __name__ == "__main__":
    run_bot()
