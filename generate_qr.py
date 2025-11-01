import qrcode

bot_username = "BirKundaBirSuhbatBot"

uz_topics = ["salomlashish", "tanishtirish"]
jp_topics = ["aisatsu", "jikoshoukai"]

for topic in uz_topics:
    url = f"https://t.me/{bot_username}?start=uz_{topic}"
    img = qrcode.make(url)
    img.save(f"qr_codes/uz_{topic}.png")

for topic in jp_topics:
    url = f"https://t.me/{bot_username}?start=jp_{topic}"
    img = qrcode.make(url)
    img.save(f"qr_codes/jp_{topic}.png")

print("✅ QR kodlar yaratildi!")
