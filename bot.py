import os
import json
import asyncio
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart
from aiogram.types import FSInputFile, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# ======================= .env yuklash =======================
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ======================= Sozlamalar =======================
CHANNEL_USERNAME = "@su_academya"
AUDIO_DIR = {"uz": "./audios/uz/", "jp": "./audios/jp/"}
USER_DATA_FILE = "user_data.json"
PAGE_SIZE = 5
BOOK_IMAGE = "./images/photo_2025-02-01_20-52-03.jpg"
BOT_IMAGE = "./images/photo_2025-02-01_20-52-03.jpg"

# ======================= Foydalanuvchi ma'lumotlari =======================
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
        keyboard=[[KeyboardButton(text="🇺🇿 UZ"), KeyboardButton(text="🇯🇵 JP")]],
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
    kb_buttons = [[KeyboardButton(text=f"{idx+1} - {audio_name}")] for idx, audio_name in enumerate(audios[start:end], start=start)]
    nav_buttons = []
    if page > 0:
        nav_buttons.append(KeyboardButton(text="⬅️ Orqaga" if lang=="uz" else "⬅️ 前へ"))
    if end < len(audios):
        nav_buttons.append(KeyboardButton(text="➡️ Keyingi" if lang=="uz" else "➡️ 次へ"))
    if nav_buttons:
        kb_buttons.append(nav_buttons)
    kb_buttons.append([KeyboardButton(text="🔙 Orqaga" if lang=="uz" else "🔙 戻る")])
    return ReplyKeyboardMarkup(keyboard=kb_buttons, resize_keyboard=True)

def get_subscription_keyboard(lang="uz"):
    if lang == "uz":
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📢 Kanalga o‘tish", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")],
            [InlineKeyboardButton(text="✅ Obuna bo‘ldim", callback_data="check_subscription")]
        ])
    else:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📢 チャンネルに移動", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")],
            [InlineKeyboardButton(text="✅ 登録しました", callback_data="check_subscription")]
        ])

def get_buy_button(lang="uz"):
    url = "https://asaxiy.uz/uz/product/ergashboy-masharipov-bir-kunda-bir-suhbat-yapon-tilida-urganing"
    text = "📖 Kitobni xarid qilish" if lang=="uz" else "📖 本を購入する"
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=text, url=url)]])

# ======================= Obuna tekshirish =======================
async def is_user_subscribed(user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# ======================= START handler =======================
@dp.message(CommandStart())
async def start_handler(message: types.Message, command: CommandStart):
    args = (command.args or "").lower()
    user_data = load_user_data()
    user_id = str(message.from_user.id)

    if user_id not in user_data:
        user_data[user_id] = {"lang": "uz", "last_audio_page": 0}

    # === QR orqali audio ochish ===
    if "_" in args and "audio" in args:
        try:
            lang, audio_str = args.split("_")
            audio_index = int(audio_str.replace("audio", "")) - 1
            if lang not in AUDIO_DIR:
                lang = "uz"
            audio_dir = AUDIO_DIR[lang]
            audios = sorted(os.listdir(audio_dir))
            if 0 <= audio_index < len(audios):
                audio_path = os.path.join(audio_dir, audios[audio_index])
                await message.answer("🎧 Audio dars yuklanmoqda..." if lang=="uz" else "🎧 オーディオレッスンを読み込み中...")
                await message.answer_audio(FSInputFile(audio_path), caption=audios[audio_index])
                user_data[user_id]["lang"] = lang
                save_user_data(user_data)
                return
        except Exception as e:
            print("QR audio xatosi:", e)

    # === Oddiy start ===
    await message.answer(
        "Xush kelibsiz! Millatingizni tanlang / ようこそ！国籍を選んでください:",
        reply_markup=get_language_keyboard()
    )

# ======================= Til tanlash =======================
@dp.message(F.text.in_(["🇺🇿 UZ", "🇯🇵 JP"]))
async def lang_handler(message: types.Message):
    lang = "uz" if message.text == "🇺🇿 UZ" else "jp"
    user_data = load_user_data()
    user_id = str(message.from_user.id)
    user_data[user_id]["lang"] = lang
    save_user_data(user_data)
    await message.answer("Asosiy menyu:" if lang=="uz" else "メインメニュー:", reply_markup=main_menu_keyboard(lang))

# ======================= Asosiy menyu handler =======================
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

    # === Audio darslar ===
    if text in ["🎧 Audio darslar", "🎧 オーディオレッスン"]:
        subscribed = await is_user_subscribed(user_id)
        if not subscribed:
            msg = "📢 Iltimos, avval kanalga obuna bo‘ling:" if lang=="uz" else "📢 まずチャンネルに登録してください："
            await message.answer(msg, reply_markup=get_subscription_keyboard(lang))
            return
        user_data[user_id]["last_audio_page"] = 0
        save_user_data(user_data)
        await message.answer(
            "Audio darslarni tanlang:" if lang=="uz" else "オーディオレッスンを選択:",
            reply_markup=get_audio_keyboard(audios, 0, lang)
        )
        return

    # === Sahifalash ===
    if text in ["➡️ Keyingi", "➡️ 次へ"]:
        page += 1
        max_page = (len(audios)-1) // PAGE_SIZE
        if page > max_page:
            page = max_page
        user_data[user_id]["last_audio_page"] = page
        save_user_data(user_data)
        await message.answer(
            "Audio darslarni tanlang:" if lang=="uz" else "オーディオレッスンを選択:",
            reply_markup=get_audio_keyboard(audios, page, lang)
        )
        return

    if text in ["⬅️ Orqaga", "⬅️ 前へ"]:
        page -= 1
        if page < 0:
            page = 0
        user_data[user_id]["last_audio_page"] = page
        save_user_data(user_data)
        await message.answer(
            "Audio darslarni tanlang:" if lang=="uz" else "オーディオレッスンを選択:",
            reply_markup=get_audio_keyboard(audios, page, lang)
        )
        return

    # === Audio tanlash ===
    if text.strip().split()[0].isdigit() and "-" in text:
        subscribed = await is_user_subscribed(user_id)
        if not subscribed:
            msg = "📢 Iltimos, avval kanalga obuna bo‘ling:" if lang=="uz" else "📢 まずチャンネルに登録してください："
            await message.answer(msg, reply_markup=get_subscription_keyboard(lang))
            return
        idx = int(text.split("-")[0].strip()) - 1
        if 0 <= idx < len(audios):
            audio_path = os.path.join(audio_dir, audios[idx])
            await message.answer_audio(FSInputFile(audio_path), caption=audios[idx])
        return

    # === Kitob haqida ===
    if text in ["📚 Kitob haqida", "📚 本について"]:
        caption = (
            "📘 Kitob nomi: Bir kunda bir suhbat – Yapon tilida o‘rganing\n\n"
            "Janr: Til o‘rganish, Amaliy qo‘llanma\n\n"
            "Bu kitob kundalik hayotda ishlatiladigan yapon tilidagi suhbatlarni o‘rganish uchun mo‘ljallangan."
            if lang == "uz" else
            "📘 本名: 一日一会話 – 日本語を学ぶ\n\nジャンル: 言語学習、実用ガイド\n\n"
            "この本は、日常生活で使用される日本語の会話を学ぶために作られています。"
        )
        await message.answer_photo(photo=FSInputFile(BOOK_IMAGE), caption=caption, reply_markup=get_buy_button(lang))
        return

    # === Bot haqida ===
    if text in ["🤖 Bot haqida", "🤖 ボットについて"]:
        caption = (
            "🤖 Bu bot 'Bir kunda bir suhbat' kitobiga asoslangan. Audio darslar orqali yapon tilini o‘rganing!"
            if lang == "uz" else
            "🤖 このボットは「一日一会話」という本に基づいています。オーディオレッスンで日本語を学びましょう！"
        )
        await message.answer_photo(photo=FSInputFile(BOT_IMAGE), caption=caption)
        return

    if text in ["🏠 Bosh sahifa", "🏠 ホーム"]:
        await message.answer("Millatingizni tanlang / 国籍を選んでください:", reply_markup=get_language_keyboard())
        return

    if text in ["🔙 Orqaga", "🔙 戻る"]:
        await message.answer("Asosiy menyu:" if lang=="uz" else "メインメニュー:", reply_markup=main_menu_keyboard(lang))
        return

# ======================= Callback =======================
@dp.callback_query(F.data == "check_subscription")
async def check_subscription(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    user_data = load_user_data()
    lang = user_data.get(str(user_id), {}).get("lang", "uz")
    subscribed = await is_user_subscribed(user_id)
    if subscribed:
        msg = "✅ Rahmat! Siz kanalga obuna bo‘ldingiz." if lang=="uz" else "✅ 登録ありがとうございます！"
        await callback.message.edit_text(msg)
    else:
        alert = "Siz hali obuna bo‘lmagansiz ❌" if lang=="uz" else "❌ まだチャンネルに登録していません。"
        await callback.answer(alert, show_alert=True)

# ======================= Main =======================
async def main():
    print("✅ Bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
