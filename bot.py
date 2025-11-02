import os
import json
import asyncio
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart
from aiogram.types import (
    FSInputFile, ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)

# ======================= Sozlamalar =======================
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

CHANNEL_USERNAME = "@su_academya"
AUDIO_DIR = {"uz": "./audios/uz/", "jp": "./audios/jp/"}
BOOK_IMAGE = "./images/photo_2025-02-01_20-52-03.jpg"
BOT_IMAGE = "./images/photo_2025-02-01_20-52-03.jpg"
USER_DATA_FILE = "user_data.json"
PAGE_SIZE = 5

# ======================= JSON ma'lumotlar =======================
def load_user_data():
    if not os.path.exists(USER_DATA_FILE):
        return {}
    with open(USER_DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_user_data(data):
    with open(USER_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# ======================= Klaviaturalar =======================
def get_language_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton("🇺🇿 UZ"), KeyboardButton("🇯🇵 JP")]],
        resize_keyboard=True
    )

def main_menu_keyboard(lang="uz"):
    if lang == "uz":
        kb = [
            [KeyboardButton("🏠 Bosh sahifa"), KeyboardButton("🎧 Audio darslar")],
            [KeyboardButton("📚 Kitob haqida"), KeyboardButton("🤖 Bot haqida")]
        ]
    else:
        kb = [
            [KeyboardButton("🏠 ホーム"), KeyboardButton("🎧 オーディオレッスン")],
            [KeyboardButton("📚 本について"), KeyboardButton("🤖 ボットについて")]
        ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_audio_keyboard(audios, page=0, lang="uz"):
    start, end = page * PAGE_SIZE, (page + 1) * PAGE_SIZE
    kb = [[KeyboardButton(f"{i+1} - {audios[i]}")] for i in range(start, min(end, len(audios)))]
    nav = []
    if page > 0:
        nav.append(KeyboardButton("⬅️ Orqaga" if lang == "uz" else "⬅️ 前へ"))
    if end < len(audios):
        nav.append(KeyboardButton("➡️ Keyingi" if lang == "uz" else "➡️ 次へ"))
    if nav: kb.append(nav)
    kb.append([KeyboardButton("🔙 Orqaga" if lang == "uz" else "🔙 戻る")])
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_subscription_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("📢 Kanalga o‘tish", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")],
        [InlineKeyboardButton("✅ Obuna bo‘ldim", callback_data="check_subscription")]
    ])

def get_buy_button(lang="uz"):
    url = "https://asaxiy.uz/uz/product/ergashboy-masharipov-bir-kunda-bir-suhbat-yapon-tilida-urganing"
    text = "📖 Kitobni xarid qilish" if lang == "uz" else "📖 本を購入する"
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text, url=url)]])

# ======================= Obuna tekshirish =======================
async def is_user_subscribed(user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# ======================= START HANDLER =======================
@dp.message(CommandStart())
async def start_handler(message: types.Message, command: CommandStart):
    args = command.args or ""
    user_id = str(message.from_user.id)
    user_data = load_user_data()

    if user_id not in user_data:
        user_data[user_id] = {"lang": "uz", "last_audio_page": 0}
    lang = user_data[user_id]["lang"]

    # QR kod orqali kirish: /start audio5
    if args.lower().startswith("audio"):
        try:
            num = int(args.replace("audio", ""))
            audio_dir = AUDIO_DIR[lang]
            audios = sorted(os.listdir(audio_dir))
            if 0 < num <= len(audios):
                path = os.path.join(audio_dir, audios[num - 1])
                await message.answer("🎧 Sizga tegishli audio dars yuklanmoqda...")
                await message.answer_audio(FSInputFile(path), caption=audios[num - 1])
                await message.answer("Menyu:", reply_markup=main_menu_keyboard(lang))
                return
        except Exception as e:
            print("QR audio xatosi:", e)
            await message.answer("❌ QR kodga tegishli audio topilmadi.")

    # Oddiy /start
    await message.answer("Xush kelibsiz! Millatingizni tanlang / ようこそ！国籍を選んでください:", reply_markup=get_language_keyboard())
    save_user_data(user_data)

# ======================= Til tanlash =======================
@dp.message(F.text.in_(["🇺🇿 UZ", "🇯🇵 JP"]))
async def lang_handler(message: types.Message):
    user_id = str(message.from_user.id)
    user_data = load_user_data()
    lang = "uz" if message.text == "🇺🇿 UZ" else "jp"
    user_data[user_id]["lang"] = lang
    save_user_data(user_data)
    await message.answer("Asosiy menyu:" if lang == "uz" else "メインメニュー:", reply_markup=main_menu_keyboard(lang))

# ======================= Asosiy menyu =======================
@dp.message()
async def menu_handler(message: types.Message):
    user_id = str(message.from_user.id)
    user_data = load_user_data()
    if user_id not in user_data:
        await start_handler(message, command=CommandStart())
        return

    lang = user_data[user_id]["lang"]
    text = message.text
    audio_dir = AUDIO_DIR[lang]
    audios = sorted(os.listdir(audio_dir))
    page = user_data[user_id].get("last_audio_page", 0)

    # 🎧 Audio darslar
    if text in ["🎧 Audio darslar", "🎧 オーディオレッスン"]:
        if not await is_user_subscribed(user_id):
            await message.answer("📢 Iltimos, kanalga obuna bo‘ling:", reply_markup=get_subscription_keyboard())
            return
        user_data[user_id]["last_audio_page"] = 0
        save_user_data(user_data)
        await message.answer("Audio darslarni tanlang:" if lang == "uz" else "オーディオレッスンを選択:", reply_markup=get_audio_keyboard(audios, 0, lang))
        return

    # Sahifalar
    if text in ["➡️ Keyingi", "➡️ 次へ"]:
        page += 1
    elif text in ["⬅️ Orqaga", "⬅️ 前へ"]:
        page = max(page - 1, 0)
    elif text in ["🔙 Orqaga", "🔙 戻る"]:
        await message.answer("Asosiy menyu:" if lang == "uz" else "メインメニュー:", reply_markup=main_menu_keyboard(lang))
        return

    user_data[user_id]["last_audio_page"] = page
    save_user_data(user_data)

    if text.split()[0].isdigit() and "-" in text:
        idx = int(text.split("-")[0]) - 1
        if 0 <= idx < len(audios):
            path = os.path.join(audio_dir, audios[idx])
            await message.answer_audio(FSInputFile(path), caption=audios[idx])
        return

    if text in ["📚 Kitob haqida", "📚 本について"]:
        cap = (
            "📘 Kitob nomi: Bir kunda bir suhbat – Yapon tilida o‘rganing\n\n"
            "Janr: Til o‘rganish, Amaliy qo‘llanma\n\n"
            "Bu kitob 25 ta mavzuni o‘z ichiga olgan va yapon tilidagi kundalik suhbatlarni o‘rgatadi."
            if lang == "uz" else
            "📘 本名: 一日一会話 – 日本語を学ぶ\n\nジャンル: 言語学習、実用ガイド\n\nこの本は25のテーマで日常会話を学ぶために作られています。"
        )
        await message.answer_photo(FSInputFile(BOOK_IMAGE), caption=cap, reply_markup=get_buy_button(lang))
        return

    if text in ["🤖 Bot haqida", "🤖 ボットについて"]:
        cap = (
            "🤖 Bu bot 'Bir kunda bir suhbat' kitobiga asoslangan. Audio darslar orqali yapon tilini o‘rganing!"
            if lang == "uz" else
            "🤖 このボットは「一日一会話」に基づいて作成されました。オーディオレッスンで日本語を学びましょう！"
        )
        await message.answer_photo(FSInputFile(BOT_IMAGE), caption=cap)
        return

    if text in ["🏠 Bosh sahifa", "🏠 ホーム"]:
        await message.answer("Millatingizni tanlang / 国籍を選んでください:", reply_markup=get_language_keyboard())

    else:
        await message.answer("Tanlovni to‘g‘ri kiriting." if lang == "uz" else "正しいオプションを選択してください。")

# ======================= Callback (Obuna tekshirish) =======================
@dp.callback_query(F.data == "check_subscription")
async def check_subscription(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if await is_user_subscribed(user_id):
        await callback.message.edit_text("✅ Obuna tasdiqlandi! Endi davom etishingiz mumkin.")
    else:
        await callback.answer("❌ Siz hali obuna bo‘lmagansiz.", show_alert=True)

# ======================= Main =======================
async def main():
    print("✅ Bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
