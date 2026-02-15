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
  "corrosion": -200,      # mV
  "ultrasonikSesHizi": 3500, # m/s
  "geriSicramaSayisi": 40    # R-value
}

print(f"📡 API'ye istek gönderiliyor: {url}")
try:
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        print("✅ API Yanıtı Başarılı (200 OK)")
        data = response.json()
        print(json.dumps(data, indent=2, ensure_ascii=False))
        print("\n🎉 TEST BAŞARILI: API çalışıyor ve hesaplama yapıyor!")
        print("👉 Şimdi Supabase'i kontrol edip bu kaydın veritabanına girip girmediğine bakacağız.")
    else:
        print(f"❌ API Hatası: {response.status_code}")
        print(response.text)

except Exception as e:
    print(f"❌ Bağlantı Hatası: {e}")
    print("Sunucu açık mı? 'uvicorn main:app --reload' çalışıyor mu?")
