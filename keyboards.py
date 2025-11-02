from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Admin panel bosh menu
def admin_main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Foydalanuvchilar ro'yxati", callback_data="admin_users")],
        [InlineKeyboardButton(text="🎧 Audio qo'shish", callback_data="admin_add_audio")],
        [InlineKeyboardButton(text="📈 Statistika", callback_data="admin_stats")],
    ])

# Orqaga tugma
def back_button():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_back")]
    ])
