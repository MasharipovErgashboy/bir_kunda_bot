import os
import json
from dotenv import load_dotenv

# ======================= .env faylni yuklash =======================
load_dotenv()

USER_DATA_FILE = "user_data.json"

# Foydalanuvchi ma'lumotlarini yuklash
def load_user_data():
    if not os.path.exists(USER_DATA_FILE):
        return {}
    with open(USER_DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# Foydalanuvchi ma'lumotlarini saqlash
def save_user_data(data):
    with open(USER_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# ======================= Adminlar =======================
ADMINS = [
    int(os.getenv("ADMIN1_ID")),
]

def is_admin(user_id: int) -> bool:
    return user_id in ADMINS
