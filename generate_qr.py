import os
import qrcode

# Bot username-ni string ichida yozing
BOT_USERNAME = "BirKundaBirSuhbatBot"
BASE_URL = f"https://t.me/{BOT_USERNAME}?start="

# Audio papkalar
AUDIO_DIRS = {
    "uz": "./audios/uz/",
    "jp": "./audios/jp/"
}

# QR kodlar saqlanadigan papka
QR_OUTPUT_DIR = "./qr_codes/"
os.makedirs(QR_OUTPUT_DIR, exist_ok=True)

for lang, dir_path in AUDIO_DIRS.items():
    audios = sorted(os.listdir(dir_path))
    lang_dir = os.path.join(QR_OUTPUT_DIR, lang)
    os.makedirs(lang_dir, exist_ok=True)

    for idx, audio in enumerate(audios, start=1):
        param = f"{lang}_audio{idx}"  # Parametr til + audio raqami bilan
        full_url = BASE_URL + param

        img = qrcode.make(full_url)
        qr_filename = os.path.join(lang_dir, f"{idx}.png")
        img.save(qr_filename)
        print(f"{lang}/{idx}.png yaratildi -> {full_url}")
