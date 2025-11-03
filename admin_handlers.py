from aiogram import types, Router, F
from aiogram.filters import Command
from utils import is_admin, load_user_data
from keyboards import admin_main_menu, back_button

admin_router = Router()

# ======================= /admin komandasi =======================
@admin_router.message(Command(commands=["admin"]))
async def admin_panel(message: types.Message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        await message.answer("❌ Siz admin emassiz!")
        return
    await message.answer("Admin panelga xush kelibsiz!", reply_markup=admin_main_menu())

# ======================= Foydalanuvchilar ro'yxati =======================
@admin_router.callback_query(lambda c: c.data and c.data.startswith("admin_users"))
async def show_users(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Siz admin emassiz!", show_alert=True)
        return
    user_data = load_user_data()
    users_text = "\n".join([f"{i+1}. ID: {uid}" for i, uid in enumerate(user_data.keys())]) or "Foydalanuvchi yo'q"
    await callback.message.edit_text(f"📋 Foydalanuvchilar ro'yxati:\n{users_text}", reply_markup=back_button())

# ======================= Yangi audio qo'shish =======================
@admin_router.callback_query(lambda c: c.data and c.data.startswith("admin_add_audio"))
async def add_audio(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Siz admin emassiz!", show_alert=True)
        return
    await callback.message.edit_text(
        "🎧 Yangi audio faylni yuboring (hozir botga audio qabul qilish funksiyasi yo'q, keyinchalik qo‘shiladi)",
        reply_markup=back_button()
    )

# ======================= Bot statistika =======================
@admin_router.callback_query(lambda c: c.data and c.data.startswith("admin_stats"))
async def show_stats(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Siz admin emassiz!", show_alert=True)
        return
    user_data = load_user_data()
    total_users = len(user_data)
    await callback.message.edit_text(f"📈 Bot statistika:\nFoydalanuvchilar soni: {total_users}", reply_markup=back_button())

# ======================= Admin panelga qaytish =======================
@admin_router.callback_query(lambda c: c.data and c.data.startswith("admin_back"))
async def go_back(callback: types.CallbackQuery):
    await callback.message.edit_text("Admin panelga xush kelibsiz!", reply_markup=admin_main_menu())
