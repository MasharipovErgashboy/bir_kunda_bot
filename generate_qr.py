import os
import qrcode

# Bot username-ni string ichida yozing
BOT_USERNAME = "BirKundaBirSuhbatBot"
BASE_URL = f"https://t.me/{BOT_USERNAME}?start="

AUDIO_DIR = "./audios/uz/"  # yoki "./audios/jp/"
QR_OUTPUT_DIR = "./qr_codes/"
os.makedirs(QR_OUTPUT_DIR, exist_ok=True)

audios = sorted(os.listdir(AUDIO_DIR))

for idx, audio in enumerate(audios, start=1):
    param = f"audio{idx}"
    full_url = BASE_URL + param

    img = qrcode.make(full_url)
    img.save(os.path.join(QR_OUTPUT_DIR, f"{idx}.png"))
    print(f"{idx}.png yaratildi -> {full_url}")
