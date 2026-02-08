import requests
import json

url = "http://127.0.0.1:8000/api/risk-hesapla"
headers = {"Content-Type": "application/json"}
payload = {
    "il": "istanbul",
    "ilce": "kadikoy",
    "yapimYili": 2000,
    "katSayisi": 5,
    "zeminDukkan": "hayir",
    "bitisik": "hayir",
    "kullanimAmaci": "konut",
    "kisaKolon": "yok",
    "agirCikma": "yok",
    "planTipi": "dikdortgen",
    "hasar": "yok",
    "ultrasonikSesHizi": 3.5,
    "geriSicramaSayisi": 35,
    "corrosion": -200,
    "crackPuan": 0,
    "zeminSinifi": "Z2"
}

try:
    response = requests.post(url, json=payload)
    print(f"Status Code: {response.status_code}")
    print("Response JSON:")
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print(f"Request failed: {e}")
