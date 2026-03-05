import requests
import json
import time

# API URL
url = "http://127.0.0.1:8000/api/risk-hesapla"

# Test Verisi (Ankara/Çankaya'da hayali bir bina)
payload = {
    "il": "Ankara",
    "ilce": "Çankaya",
    "yapimYili": 2005,
    "katSayisi": 5,
    "zeminDukkan": "hayir",
    "bitisik": "hayir",
    "hasar": "yok",
    "kullanimAmaci": "konut",
    "kisaKolon": "yok",
    "agirCikma": "yok",
    "planTipi": "dikdortgen",
    "bitisikHiza": "yok",
    "zeminSinifi": "Z2",
    "crackPuan": 0,
    "corrosion": -200,  # mV
    "ultrasonikSesHizi": 3500,  # m/s
    "geriSicramaSayisi": 40,  # R-value
}

print(f">> API'ye istek gonderiliyor: {url}")
try:
    response = requests.post(url, json=payload)

    if response.status_code == 200:
        print("[BASARILI] API Yaniti Basarili (200 OK)")
        data = response.json()
        print(json.dumps(data, indent=2, ensure_ascii=False))
        print("\n>> TEST BASARILI: API calisiyor ve hesaplama yapiyor!")
        print(
            ">> Simdi Supabase'i kontrol edip bu kaydin veritabanina girip girmedigine bakacagiz."
        )
    else:
        print(f"[HATA] API Hatasi: {response.status_code}")
        print(response.text)

except Exception as e:
    print(f"[HATA] Baglanti Hatasi: {e}")
    print("Sunucu açık mı? 'uvicorn main:app --reload' çalışıyor mu?")
