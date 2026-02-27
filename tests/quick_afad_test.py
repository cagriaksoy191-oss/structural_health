"""Hızlı AFAD entegrasyon testi — daha uzun timeout ile"""
import requests

payload = {
    "il": "istanbul",
    "ilce": "Kadıköy",
    "yapimYili": 1998,
    "katSayisi": 7,
    "zeminDukkan": "hayir",
    "bitisik": "hayir",
    "hasar": "yok",
    "kullanimAmaci": "konut",
    "kisaKolon": "yok",
    "agirCikma": "yok",
    "planTipi": "dikdortgen",
    "ultrasonikSesHizi": 4.5,
    "geriSicramaSayisi": 30,
    "corrosion": -200,
}

print("API'ye istek gonderiliyor (120s timeout)...")
r = requests.post("http://127.0.0.1:8000/api/risk-hesapla", json=payload, timeout=120)
data = r.json()

print("=== AFAD Entegrasyon Test Sonuclari ===")
print(f"Status Code: {r.status_code}")
print(f"Health Score: {data.get('healthScore')}")
print(f"Deprem Seviye: {data.get('depremSeviye')}")
print(f"PGA: {data.get('pga')}")
print(f"Kaynak: {data.get('depremKaynak')}")
print(f"Genel Seviye: {data.get('genelSeviye')}")
print(f"Beton Dayanimi: {data.get('basincDayanimi')}")
print()
print("Detaylar:")
for d in data.get("detaylar", []):
    print(f"  * {d}")

print()
if data.get("depremKaynak") == "AFAD":
    print(">>> AFAD CANLI VERI CALISIYOR! <<<")
elif data.get("depremKaynak") == "Statik Harita":
    print(">>> Statik harita kullanildi (AFAD erisilemiyor, fallback calisti) <<<")
else:
    print(f">>> Kaynak: {data.get('depremKaynak')} <<<")
