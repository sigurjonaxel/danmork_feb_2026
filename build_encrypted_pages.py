#!/usr/bin/env python3
"""
Byggir dulkóðaða gagnaskrá fyrir GitHub Pages (Danmerkurferð febrúar 2027 - Sigurjón & Lóa).
Öll gögn (hótel, bílaleigubílar, þátttakendur, áfangar) eru dulkóðuð með AES-256 (PBKDF2 SHA-256)
með PIN-númerinu. Á GitHub Pages er ómögulegt að lesa gögnin án PIN.
Keyrsla: python3 build_encrypted_pages.py
"""

import os
import json
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

ENV_FILE = ".env"

def get_pin():
    pin = os.environ.get("FAMILY_PIN")
    if pin:
        return pin.strip()
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("FAMILY_PIN="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    return "2027"

def build():
    pin = get_pin()
    print(f"🔒 Dulkóða gögn fyrir Danmerkurferð á GitHub Pages með PIN: {pin}")

    # Lesa hótel- og bílaleigugögn
    with open("houses.json", "r", encoding="utf-8") as f:
        houses = json.load(f)

    # Aðeins Sigurjón og Lóa í þessari ferð
    family_members = [
        "Sigurjón Axel (Sissi)",
        "Ólafía Rósbjörg (Lóa)"
    ]

    family_birthdays = [
        { "name": "Ólafía Rósbjörg (Lóa)", "shortName": "Lóa", "avatar": "images/avatars/loa.jpg?v=2", "date": "10. janúar 1974", "dayMonth": "10. jan", "year": 1974, "age2027": 53 },
        { "name": "Sigurjón Axel (Sissi)", "shortName": "Sigurjón (Sissi)", "avatar": "images/avatars/sigurjon.jpg?v=2", "date": "4. febrúar 1974", "dayMonth": "4. feb", "year": 1974, "age2027": 53 }
    ]

    weeks = [
        { "id": "leg1", "num": "Leggur 1: Óðinsvé", "dates": "17. feb – 19. feb 2027 (2 nætur)", "tag": "Mið–Fös · 🎓 SDU · 🏙️ H.C. Andersen hverfið" },
        { "id": "leg2", "num": "Leggur 2: Rípe", "dates": "19. feb – 20. feb 2027 (1 nótt)", "tag": "Fös–Lau · 📦 IKEA varningur · 👩‍❤️‍👩 Heimsókn til vinkonu · 🏰 Ribe Domkirke" },
        { "id": "leg3", "num": "Leggur 3: Álaborg", "dates": "20. feb – 22. feb 2027 (2 nætur)", "tag": "Lau–Mán · 🎓 AAU · 🌊 Limfjörðurinn & Utzon Center" },
        { "id": "leg4", "num": "Leggur 4: Óðinsvé", "dates": "22. feb – 23. feb 2027 (1 nótt)", "tag": "Mán–Þri · 🍽️ Lokakvöld í Odense áður en flogið er heim" },
        { "id": "car", "num": "🚗 Bílaleigubíll CPH", "dates": "17. feb – 23. feb 2027 (6 dagar)", "tag": "Kastrup (CPH) · ~935 km akstur · 📦 Pláss fyrir IKEA varning" }
    ]

    payload = {
        "familyMembers": family_members,
        "familyBirthdays": family_birthdays,
        "weeks": weeks,
        "houses": houses
    }

    raw_bytes = json.dumps(payload, ensure_ascii=False).encode("utf-8")

    # AES-256 GCM með PBKDF2
    salt = os.urandom(16)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000
    )
    key = kdf.derive(pin.encode("utf-8"))
    iv = os.urandom(12)
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(iv, raw_bytes, None)

    encrypted_payload = {
        "salt": base64.b64encode(salt).decode("utf-8"),
        "iv": base64.b64encode(iv).decode("utf-8"),
        "data": base64.b64encode(ciphertext).decode("utf-8")
    }

    with open("encrypted_data.json", "w", encoding="utf-8") as f:
        json.dump(encrypted_payload, f, indent=2)

    print("✅ encrypted_data.json búin til! Gögnin eru 100% dulkóðuð fyrir GitHub Pages.")

if __name__ == "__main__":
    build()
