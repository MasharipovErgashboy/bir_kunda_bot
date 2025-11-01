import os
import json
import asyncio
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.types import FSInputFile, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

BOT_TOKEN = "8079459948:AAHkwlSfKZ8Sl4RIrlYkEvRGzVJnaWp6Gn4"
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# AUDIO DIREKTORI
AUDIO_DIR = {
    "uz": "./audios/uz/",
    "jp": "./audios/jp/"
}

# USER DATA
USER_DATA_FILE = "user_data.json"

def load_user_data():
    if not os.path.exists(USER_DATA_FILE):
        return {}
    with open(USER_DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_user_data(data):
    with open(USER_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# ======================= KEYBOARDS =======================

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
    page_size = 5
    start = page * page_size
    end = start + page_size
    kb_buttons = [[KeyboardButton(text=f"{idx+1} - {audio_name}")] for idx, audio_name in enumerate(audios[start:end], start=start)]
    
    nav_buttons = []
    if page > 0:
        nav_buttons.append(KeyboardButton(text="⬅️ Orqaga" if lang=="uz" else "⬅️ 前へ"))
    if end < len(audios):
        nav_buttons.append(KeyboardButton(text="➡️ Keyingi" if lang=="uz" else "➡️ 次へ"))
    
    if nav_buttons:
        kb_buttons.append(nav_buttons)
    
    # Har doim mavjud Orqaga button
    kb_buttons.append([KeyboardButton(text="🔙 Orqaga") if lang=="uz" else KeyboardButton(text="🔙 戻る")])
    return ReplyKeyboardMarkup(keyboard=kb_buttons, resize_keyboard=True)

# ======================= HANDLERS =======================

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer(
        "Xush kelibsiz! Millatingizni tanlang / ようこそ！国籍を選んでください:",
        reply_markup=get_language_keyboard()
    )

@dp.message(F.text.in_(["🇺🇿 UZ", "🇯🇵 JP"]))
async def lang_handler(message: types.Message):
    lang = "uz" if message.text == "🇺🇿 UZ" else "jp"
    user_data = load_user_data()
    user_id = str(message.from_user.id)
    user_data[user_id] = {"lang": lang, "last_audio_page": 0}
    save_user_data(user_data)

    text = "Asosiy menyu:" if lang=="uz" else "メインメニュー:"
    await message.answer(text, reply_markup=main_menu_keyboard(lang))

@dp.message()
async def main_menu_handler(message: types.Message):
    user_data = load_user_data()
    user_id = str(message.from_user.id)
    if user_id not in user_data:
        await start_handler(message)
        return
    lang = user_data[user_id]["lang"]
    text = message.text

    # Bosh sahifa
    if text in ["🏠 Bosh sahifa","🏠 ホーム"]:
        await message.answer(
            "Millatingizni tanlang / 国籍を選んでください:",
            reply_markup=get_language_keyboard()
        )
        return

    # Audio darslar
    if text in ["🎧 Audio darslar","🎧 オーディオレッスン"]:
        audio_dir = AUDIO_DIR[lang]
        audios = sorted(os.listdir(audio_dir))
        if not audios:
            await message.answer("Audio mavjud emas / オーディオがありません。")
            return
        user_data[user_id]["last_audio_page"]=0
        save_user_data(user_data)
        first_audio = os.path.join(audio_dir, audios[0])
        await message.answer_audio(FSInputFile(first_audio), caption=audios[0])
        await message.answer("Audio darslarni tanlang:" if lang=="uz" else "オーディオレッスンを選択:", reply_markup=get_audio_keyboard(audios, page=0, lang=lang))
        return

    # Bot haqida
    if text in ["🤖 Bot haqida","🤖 ボットについて"]:
        bot_text = (
            "🤖 Bu bot 'Bir kunda bir suhbat' kitobiga asoslangan.\n\n"
            "Bot yordamida siz:\n"
            "- Audio darslarni tinglashingiz,\n"
            "- Kitob haqida ma'lumot olishingiz,\n"
            "- Oson va interaktiv tarzda yapon tilini o‘rganishingiz mumkin."
        ) if lang=="uz" else (
            "🤖 このボットは「一日一会話」の本に基づいています。\n\n"
            "このボットを使うと:\n"
            "- オーディオレッスンを聞くことができます。\n"
            "- 本の情報を取得できます。\n"
            "- 簡単でインタラクティブに日本語を学べます。"
        )
        await message.answer(bot_text)
        return

    # Kitob haqida
    if text in ["📚 Kitob haqida","📚 本について"]:
        book_image_path = "./images/photo_2025-02-01_20-52-03.jpg"
        if os.path.exists(book_image_path):
            await message.answer_photo(FSInputFile(book_image_path))
        book_text = (
            "📖 'Bir kunda bir suhbat' kitobi:\n"
            "- Kitobda 25 ta mavzu orqali kundalik suhbatlar mavjud.\n"
            "- Kitob harid qilishingiz mumkin quyidagi tugma orqali."
        ) if lang=="uz" else (
            "📖「一日一会話」:\n"
            "- 25のテーマを通して日常会話を学べます。\n"
            "- 下のボタンから購入できます。"
        )
        buy_button = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Kitob xarid qilish" if lang=="uz" else "購入する", url="https://asaxiy.uz/uz/product/ergashboy-masharipov-bir-kunda-bir-suhbat-yapon-tilida-urganing")]
        ])
        await message.answer(book_text, reply_markup=buy_button)
        return

    # Audio navigation
    user_id = str(message.from_user.id)
    if user_id not in user_data:
        await start_handler(message)
        return
    lang = user_data[user_id]["lang"]
    audio_dir = AUDIO_DIR[lang]
    audios = sorted(os.listdir(audio_dir))
    page = user_data[user_id].get("last_audio_page",0)

    # Orqaga va oldinga
    if text in ["⬅️ Orqaga","⬅️ 前へ"]:
        page = max(page - 1, 0)
    elif text in ["➡️ Keyingi","➡️ 次へ"]:
        max_page = (len(audios)-1)//5
        page = min(page + 1, max_page)
    elif text in ["🔙 Orqaga","🔙 戻る"]:
        await message.answer("Asosiy menyu:" if lang=="uz" else "メインメニュー:", reply_markup=main_menu_keyboard(lang))
        return
    else:
        # Audio tanlash
        try:
            idx = int(text.split("-")[0].strip()) - 1
            audio_path = os.path.join(audio_dir, audios[idx])
            await message.answer_audio(FSInputFile(audio_path), caption=audios[idx])
        except:
            await message.answer("Iltimos tugmani to‘g‘ri tanlang / 正しいボタンを選んでください。")
            return

    user_data[user_id]["last_audio_page"] = page
    save_user_data(user_data)
    await message.answer("Audio darslarni tanlang:" if lang=="uz" else "オーディオレッスンを選択:", reply_markup=get_audio_keyboard(audios, page=page, lang=lang))

# ======================= MAIN =======================
async def main():
    print("Bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
