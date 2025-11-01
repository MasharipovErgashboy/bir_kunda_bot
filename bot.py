import os
import json
import asyncio
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart
from aiogram.types import FSInputFile, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# ======================= .env =======================
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ======================= Sozlamalar =======================
CHANNEL_USERNAME = "@su_academya"
AUDIO_DIR = {"uz": "./audios/uz/", "jp": "./audios/jp/"}
USER_DATA_FILE = "user_data.json"
PAGE_SIZE = 5  # audio sahifa hajmi

# ======================= JSON boshqaruvi =======================
def load_user_data():
    if not os.path.exists(USER_DATA_FILE):
        return {}
    with open(USER_DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_user_data(data):
    with open(USER_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# ======================= Klaviaturalar =======================
def get_language_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🇺🇿 UZ")],
            [KeyboardButton(text="🇯🇵 JP")]
        ],
        resize_keyboard=True
    )

def main_menu_keyboard(lang="uz"):
    if lang == "uz":
        keyboard = [
            [KeyboardButton(text="🏠 Bosh sahifa"), KeyboardButton(text="🎧 Audio darslar")],
            [KeyboardButton(text="🤖 Bot haqida"), KeyboardButton(text="📚 Kitob haqida")]
        ]
    else:
        keyboard = [
            [KeyboardButton(text="🏠 ホーム"), KeyboardButton(text="🎧 オーディオレッスン")],
            [KeyboardButton(text="🤖 ボットについて"), KeyboardButton(text="📚 本について")]
        ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def get_audio_keyboard(audios, page=0, lang="uz"):
    start = page * PAGE_SIZE
    end = start + PAGE_SIZE
    kb_buttons = [
        [KeyboardButton(text=f"{idx+1} - {audio_name}")]
        for idx, audio_name in enumerate(audios[start:end], start=start)
    ]
    nav_buttons = []
    if page > 0:
        nav_buttons.append(KeyboardButton(text="⬅️ Orqaga" if lang=="uz" else "⬅️ 前へ"))
    if end < len(audios):
        nav_buttons.append(KeyboardButton(text="➡️ Keyingi" if lang=="uz" else "➡️ 次へ"))
    if nav_buttons:
        kb_buttons.append(nav_buttons)
    kb_buttons.append([KeyboardButton(text="🔙 Orqaga") if lang=="uz" else KeyboardButton(text="🔙 戻る")])
    return ReplyKeyboardMarkup(keyboard=kb_buttons, resize_keyboard=True)

def get_subscription_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Kanalga o‘tish", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")],
        [InlineKeyboardButton(text="✅ Obuna bo‘ldim", callback_data="check_subscription")]
    ])

# ======================= Kanal obunasini tekshirish =======================
async def is_user_subscribed(user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# ======================= START handler =======================
@dp.message(CommandStart())
async def start_handler(message: types.Message, command: CommandStart):
    args = command.args or ""
    user_data = load_user_data()
    user_id = str(message.from_user.id)

    if user_id not in user_data:
        user_data[user_id] = {"lang": None, "last_audio_page": 0, "pending_audio": None}

    # QR koddan kelgan audio
    if args.lower().startswith("audio"):
        try:
            audio_index = int(args[5:]) - 1
            user_data[user_id]["pending_audio"] = audio_index
        except:
            user_data[user_id]["pending_audio"] = None

    save_user_data(user_data)

    await message.answer(
        "Xush kelibsiz! Millatingizni tanlang / ようこそ！国籍を選んでください:",
        reply_markup=get_language_keyboard()
    )

# ======================= Til tanlash =======================
@dp.message(F.text.in_(["🇺🇿 UZ","🇯🇵 JP"]))
async def lang_handler(message: types.Message):
    lang = "uz" if message.text=="🇺🇿 UZ" else "jp"
    user_data = load_user_data()
    user_id = str(message.from_user.id)

    user_data[user_id]["lang"] = lang
    save_user_data(user_data)

    await message.answer("Asosiy menyu:" if lang=="uz" else "メインメニュー:", reply_markup=main_menu_keyboard(lang))

    # QR koddan kelgan audio avtomatik
    pending_audio = user_data[user_id].get("pending_audio")
    audio_dir = AUDIO_DIR[lang]
    audios = sorted(os.listdir(audio_dir))
    if pending_audio is not None and 0 <= pending_audio < len(audios):
        page = pending_audio // PAGE_SIZE
        user_data[user_id]["last_audio_page"] = page
        save_user_data(user_data)
        await message.answer(
            "Audio darslarni tanlang:" if lang=="uz" else "オーディオレッスンを選択:",
            reply_markup=get_audio_keyboard(audios, page=page, lang=lang)
        )
        audio_path = os.path.join(audio_dir, audios[pending_audio])
        await message.answer_audio(FSInputFile(audio_path), caption=audios[pending_audio])
        user_data[user_id]["pending_audio"] = None
        save_user_data(user_data)

# ======================= Asosiy menyu =======================
@dp.message()
async def main_menu_handler(message: types.Message):
    user_data = load_user_data()
    user_id = str(message.from_user.id)
    if user_id not in user_data:
        await start_handler(message, command=CommandStart())
        return

    lang = user_data[user_id]["lang"]
    text = message.text
    audio_dir = AUDIO_DIR[lang]
    audios = sorted(os.listdir(audio_dir))
    page = user_data[user_id].get("last_audio_page", 0)

    # Audio darslar
    if text in ["🎧 Audio darslar","🎧 オーディオレッスン"]:
        subscribed = await is_user_subscribed(user_id)
        if not subscribed:
            await message.answer("📢 Iltimos, avval kanalga obuna bo‘ling:", reply_markup=get_subscription_keyboard())
            return
        if not audios:
            await message.answer("Audio mavjud emas / オーディオがありません。")
            return
        await message.answer(
            "Audio darslarni tanlang:" if lang=="uz" else "オーディオレッスンを選択:",
            reply_markup=get_audio_keyboard(audios, page=page, lang=lang)
        )
        return

    # Sahifalash
    if text in ["➡️ Keyingi","➡️ 次へ"]:
        page += 1
        max_page = (len(audios)-1)//PAGE_SIZE
        if page > max_page: page = max_page
        user_data[user_id]["last_audio_page"] = page
        save_user_data(user_data)
        await message.answer(
            "Audio darslarni tanlang:" if lang=="uz" else "オーディオレッスンを選択:",
            reply_markup=get_audio_keyboard(audios, page=page, lang=lang)
        )
        return
    if text in ["⬅️ Orqaga","⬅️ 前へ"]:
        page -= 1
        if page < 0: page = 0
        user_data[user_id]["last_audio_page"] = page
        save_user_data(user_data)
        await message.answer(
            "Audio darslarni tanlang:" if lang=="uz" else "オーディオレッスンを選択:",
            reply_markup=get_audio_keyboard(audios, page=page, lang=lang)
        )
        return

    # Audio tanlash (faqat foydalanuvchi bosganda)
    if text.strip().split()[0].isdigit() and "-" in text:
        subscribed = await is_user_subscribed(user_id)
        if not subscribed:
            await message.answer("📢 Iltimos, avval kanalga obuna bo‘ling:", reply_markup=get_subscription_keyboard())
            return
        idx = int(text.split("-")[0].strip()) - 1
        if 0 <= idx < len(audios):
            audio_path = os.path.join(audio_dir, audios[idx])
            await message.answer_audio(FSInputFile(audio_path), caption=audios[idx])
        return

    # Kitob haqida
    if text in ["📚 Kitob haqida","📚 本について"]:
        await message.answer("Kitob haqida matn shu yerda…")
        return

    # Bot haqida
    if text in ["🤖 Bot haqida","🤖 ボットについて"]:
        await message.answer("Bot haqida matn shu yerda…")
        return

    # Menyu tugmalari
    if text in ["🏠 Bosh sahifa","🏠 ホーム"]:
        await message.answer("Millatingizni tanlang / 国籍を選んでください:", reply_markup=get_language_keyboard())
    elif text in ["🔙 Orqaga","🔙 戻る"]:
        await message.answer("Asosiy menyu:", reply_markup=main_menu_keyboard(lang))

# Callbacklar
@dp.callback_query(F.data=="check_subscription")
async def check_subscription(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    subscribed = await is_user_subscribed(user_id)
    if subscribed:
        await callback.message.edit_text("✅ Rahmat! Siz kanalga obuna bo‘lgansiz.")
    else:
        await callback.answer("Siz hali obuna bo‘lmagansiz ❌", show_alert=True)

# MAIN
async def main():
    print("✅ Bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
