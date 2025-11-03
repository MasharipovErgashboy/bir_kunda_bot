import os
import json
from dotenv import load_dotenv

# ======================= .env faylni yuklash =======================
load_dotenv()

USER_DATA_FILE = "user_data.json"

# ======================= Foydalanuvchi ma'lumotlarini boshqarish =======================
def load_user_data() -> dict:
    """
    Foydalanuvchi ma'lumotlarini JSON fayldan yuklaydi.
    Agar fayl mavjud bo'lmasa, bo'sh lug'at qaytaradi.
    """
    if not os.path.exists(USER_DATA_FILE):
        return {}
    with open(USER_DATA_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            # Agar fayl bo'sh yoki noto'g'ri JSON bo'lsa
            return {}

def save_user_data(data: dict) -> None:
    """
    Foydalanuvchi ma'lumotlarini JSON faylga saqlaydi.
    """
    with open(USER_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# ======================= Adminlar =======================
# .env fayldan admin IDlarini olish
admin_id = os.getenv("ADMIN1_ID")  # bitta admin uchun
ADMINS = [int(admin_id)] if admin_id and admin_id.isdigit() else []

def is_admin(user_id: int) -> bool:
    """
    Foydalanuvchi admin ekanligini tekshiradi.
    """
    return user_id in ADMINS
