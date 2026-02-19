import sys
import os

# Add parent directory to path to import main
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import RiskRequest

payload = {
    "il": "Istanbul",
    "ilce": "Kadikoy",
    "yapimYili": 2005,
    "katSayisi": 5,
    "zeminDukkan": "evet",
    "bitisik": "hayir",
    "hasar": "yok",
    "kullanimAmaci": "konut",
    "kisaKolon": "hayir",
    "agirCikma": "var",
    "planTipi": "dikdortgen",
    "bitisikHiza": "yok",
    "ultrasonikSesHizi": 4500.5,
    "geriSicramaSayisi": 12.3,
    "corrosion": 0.1,
    "zeminSinifi": "Z2",
    "crackPuan": 2,
}

try:
    RiskRequest(**payload)
    print("Payload is VALID!")
except Exception as e:
    print(f"Validation Error: {e}")
