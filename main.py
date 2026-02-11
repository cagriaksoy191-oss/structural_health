from typing import List, Optional, Literal, Tuple, Dict
from pathlib import Path
from datetime import datetime
import csv
import threading
import unicodedata

import pandas as pd
import joblib
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

# -------------------------------------------------
#  UYGULAMA VE AYARLAR
# -------------------------------------------------
app = FastAPI(title="Yapı Sağlığı Ön Tarama API")

# --- CORS AYARLARI ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- AI CONFIG (Qwen3) ---
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen3:8b"

# --- CSV THREAD LOCK ---
# Not: Sunum sırasında (tek worker) bu kilit dosyayı korur.
CSV_LOCK = threading.Lock()


# -------------------------------------------------
#  PYDANTIC MODELLERİ (Validasyonlu)
# -------------------------------------------------
class RiskRequest(BaseModel):
    il: str
    ilce: Optional[str] = ""

    # Dinamik yıl kontrolü
    yapimYili: int = Field(..., ge=1800)

    @field_validator("yapimYili")
    @classmethod
    def check_year_not_future(cls, v: int):
        current_year = datetime.now().year
        if v > current_year:
            raise ValueError(f"Yapım yılı gelecekte olamaz (En fazla {current_year}).")
        return v

    katSayisi: int = Field(..., ge=1, le=100)

    zeminDukkan: Literal["evet", "hayir"]
    bitisik: Literal["evet", "hayir"]
    hasar: Literal["yok", "hafif", "kolon"]

    kullanimAmaci: Literal["konut", "isyeri", "okul", "hastane", "sanayi", "diger"]

    kisaKolon: Literal["yok", "var", "emin_degil"]
    agirCikma: Literal["yok", "hafif", "buyuk"]
    planTipi: Literal["dikdortgen", "L", "T", "U", "kompleks"]
    bitisikHiza: Optional[Literal["uyumlu", "farkli", "yok"]] = "yok"

    # Beton Girdileri (Pozitif olmalı)
    ultrasonikSesHizi: float = Field(..., gt=0)
    geriSicramaSayisi: float = Field(..., gt=0)

    # Korozyon Girdisi
    # Sınırı Fuzzy'den biraz geniş tuttuk ki aşırı değerlerde hata vermesin, clamp yapıp uyaralım.
    corrosion: float = Field(..., description="Korozyon potansiyeli (mV)")
    
    # "Otomatik" seçilirse boş gelebilir.
    zeminSinifi: Optional[str] = None

    # Frontend verileri
    crackPuan: Optional[int] = Field(default=None, ge=0, le=3)


class RiskResponse(BaseModel):
    healthScore: int
    genelSeviye: str
    aciklama: str
    depremSeviye: str
    depremPuan: int
    yapisalSeviye: str
    yapisalPuan: int
    toplamYapisalRisk: int
    zeminSinifi: Optional[str]
    basincDayanimi: Optional[float] = None
    detaylar: List[str]

    fuzzyLabel: str
    corrosion: float

    aiEtiket: Optional[str] = None
    aiYorum: Optional[str] = None


# -------------------------------------------------
#  AKILLI NORMALİZASYON (V12)
# -------------------------------------------------
def normalize_key(text: Optional[str]) -> str:
    """
    Türkçe karakterleri güvenli İngilizce karakterlere çevirir.
    Optional[str] tip desteği eklendi.
    """
    if not text:
        return ""

    # Türkçe Karakter Eşleşmesi
    tr_map = str.maketrans({
        "ğ": "g", "Ğ": "g",
        "ı": "i", "İ": "i", "I": "i",
        "ö": "o", "Ö": "o",
        "ş": "s", "Ş": "s",
        "ü": "u", "Ü": "u",
        "ç": "c", "Ç": "c"
    })

    text = text.strip().translate(tr_map).lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.replace(" ", "").replace("-", "")

    return text


# -------------------------------------------------
#  YAPAY ZEKA FONKSİYONLARI
# -------------------------------------------------
# -------------------------------------------------
#  YAPAY ZEKA FONKSİYONLARI (CHAT MODU - GARANTİ)
# -------------------------------------------------
def get_llm_comment(skor, risk_durumu, beton, korozyon, risk_puani):
    # Bilgisayarındaki model adı (Listede gördüğün ismin aynısı olmalı)
    MODEL_ADI = "qwen3:8b"

    # Kullanıcı verilerini hazırlayalım
    user_message = f"""
    ANALİZ EDİLECEK BİNA VERİLERİ:
    - Yapı Sağlık Skoru: {skor}/100
    - Risk Durumu: {risk_durumu}
    - Beton Dayanımı: {beton} MPa
    - Korozyon Durumu: {korozyon} mV
    - Genel Risk Puanı: {risk_puani}

    GÖREVİN:
    Bu verileri inceleyen uzman bir inşaat mühendisi gibi davran. 
    Bina sahibi için GÜVEN VEREN, AKICI, PROFESYONEL ve TÜRKÇE bir değerlendirme paragrafı yaz.
    Madde madde yazma, tek bir bütün metin olsun.
    """

    # Sistem (Rol) Tanımı
    system_message = "Sen uzman bir Türk inşaat mühendisisin. Teknik terimleri halkın anlayacağı dilde, akıcı bir paragraf olarak yorumlarsın."

    try:
        # ARTIK '/api/chat' KULLANIYORUZ (Daha kararlı)
        response = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": MODEL_ADI,
                "messages": [
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                "stream": False,
                "options": {"temperature": 0.7}  # Biraz yaratıcılık verelim ki konuşsun
            },
            timeout=120
        )

        if response.status_code == 200:
            # Chat modunda cevap 'message' -> 'content' içindedir
            return response.json()['message']['content'].strip()
        else:
            return f"⚠️ Bağlantı Hatası (Kod: {response.status_code}). Ollama açık mı?"

    except Exception as e:
        return f"⚠️ Yapay Zeka Cevap Vermedi: {str(e)}"

# -------------------------------------------------
#  FUZZY LOGIC SİSTEMİ
# -------------------------------------------------
def create_fuzzy_system():
    strength = ctrl.Antecedent(np.arange(0, 81, 1), 'strength')
    corrosion = ctrl.Antecedent(np.arange(-600, 101, 1), 'corrosion')
    survey_risk = ctrl.Antecedent(np.arange(0, 51, 1), 'survey_risk')
    health = ctrl.Consequent(np.arange(0, 101, 1), 'health')

    strength['low'] = fuzz.trapmf(strength.universe, [0, 0, 15, 25])
    strength['medium'] = fuzz.trimf(strength.universe, [20, 35, 50])
    strength['high'] = fuzz.trapmf(strength.universe, [40, 55, 80, 80])

    corrosion['high_risk'] = fuzz.trapmf(corrosion.universe, [-600, -600, -400, -300])
    corrosion['medium_risk'] = fuzz.trimf(corrosion.universe, [-400, -275, -150])
    corrosion['low_risk'] = fuzz.trapmf(corrosion.universe, [-200, -100, 100, 100])

    survey_risk['safe'] = fuzz.trapmf(survey_risk.universe, [0, 0, 10, 15])
    survey_risk['medium'] = fuzz.trimf(survey_risk.universe, [12, 25, 38])
    survey_risk['high'] = fuzz.trapmf(survey_risk.universe, [30, 40, 50, 50])

    health['very_bad'] = fuzz.trimf(health.universe, [0, 0, 25])
    health['bad'] = fuzz.trimf(health.universe, [20, 35, 50])
    health['medium'] = fuzz.trimf(health.universe, [45, 55, 65])
    health['good'] = fuzz.trimf(health.universe, [60, 75, 90])
    health['very_good'] = fuzz.trimf(health.universe, [80, 100, 100])

    # Kurallar
    rule_very_bad = ctrl.Rule(
        (corrosion['high_risk']) | (strength['low'] & survey_risk['high']) | (
                    strength['low'] & corrosion['medium_risk']), health['very_bad'])
    rule_bad = ctrl.Rule(
        (strength['low'] & survey_risk['medium'] & corrosion['low_risk']) | (
                    strength['medium'] & survey_risk['high'] & corrosion['low_risk']) | (
                    corrosion['medium_risk'] & strength['medium']), health['bad'])
    rule_medium = ctrl.Rule(
        (strength['medium'] & survey_risk['medium'] & corrosion['low_risk']) | (
                    strength['high'] & survey_risk['high'] & corrosion['low_risk']) | (
                    corrosion['medium_risk'] & strength['high']), health['medium'])
    rule_good = ctrl.Rule(
        (strength['high'] & survey_risk['medium'] & corrosion['low_risk']) | (
                    strength['medium'] & survey_risk['safe'] & corrosion['low_risk']), health['good'])
    rule_very_good = ctrl.Rule(
        (strength['high'] & survey_risk['safe'] & corrosion['low_risk']), health['very_good'])

    return ctrl.ControlSystem([rule_very_bad, rule_bad, rule_medium, rule_good, rule_very_good])


fuzzy_control_system = create_fuzzy_system()


def get_fuzzy_label(score: float) -> str:
    if score < 25: return "Very Bad (Çok Kötü - Acil)"
    if score < 45: return "Bad (Kötü - Güçlendirme Gerekli)"
    if score < 65: return "Medium (Orta Risk - İnceleme Gerekli)"
    if score < 85: return "Good (İyi - Bakım Önerilir)"
    return "Very Good (Çok İyi - Sağlam)"


def clamp(val: float, low: float, high: float) -> float:
    return max(low, min(high, val))


# -------------------------------------------------
#  BETON MODELİ
# -------------------------------------------------
CONCRETE_MODEL_PATH = Path("concrete_model.joblib")
concrete_model = None
try:
    if CONCRETE_MODEL_PATH.exists():
        concrete_model = joblib.load(CONCRETE_MODEL_PATH)
        print("✅ Beton Modeli (RandomForest) yüklendi.")
    else:
        print("⚠️ Beton Modeli bulunamadı.")
except Exception as e:
    print(f"Model yükleme hatası: {e}")


def tahmin_beton_dayanimi(upv: float, rn: float) -> float:
    if concrete_model is None: return 25.0
    try:
        res = concrete_model.predict(pd.DataFrame({"UPV": [upv], "RN": [rn]}))[0]
        return float(res)
    except:
        return 25.0


# -------------------------------------------------
#  HARİTA VERİLERİ (RAW)
# -------------------------------------------------
DEPREM_RISK_MAP_RAW = {
    "istanbul": {"_default": "yüksek", "arnavutköy": "düşük", "sarıyer": "orta", "eyüpsultan": "orta",
                 "beykoz": "düşük", "şile": "düşük", "çatalca": "orta", "başakşehir": "orta", "avcılar": "yüksek",
                 "bakırköy": "yüksek", "küçükçekmece": "yüksek", "zeytinburnu": "yüksek", "fatih": "yüksek",
                 "kadıköy": "yüksek", "maltepe": "yüksek", "kartal": "yüksek", "tuzla": "yüksek", "pendik": "yüksek",
                 "adalar": "yüksek", "büyükçekmece": "yüksek", "silivri": "yüksek", "esenler": "orta",
                 "sultangazi": "orta"},
    "ankara": {"_default": "düşük", "elmadağ": "orta", "nallıhan": "yüksek", "beypazarı": "orta", "kazan": "orta",
               "kızılcahamam": "yüksek", "çamlıdere": "yüksek", "evren": "orta", "bala": "orta"},
    "izmir": {"_default": "yüksek", "kiraz": "orta", "beydağ": "orta", "karaburun": "orta"},
    "manisa": {"_default": "yüksek", "demirci": "orta", "gördes": "orta"},
    "aydın": {"_default": "yüksek"},
    "muğla": {"_default": "yüksek", "datça": "orta"},
    "antalya": {"_default": "orta", "demre": "yüksek", "finike": "yüksek", "kumluca": "yüksek", "kemer": "yüksek",
                "kaş": "yüksek", "alanya": "düşük", "gündoğmuş": "düşük", "gazipaşa": "düşük"},
    "adana": {"_default": "yüksek", "tufanbeyli": "orta", "saimbeyli": "orta", "pozantı": "orta"},
    "hatay": {"_default": "yüksek"},
    "kahramanmaraş": {"_default": "yüksek", "ekinözü": "orta"},
    "erzincan": {"_default": "yüksek"},
    "bingöl": {"_default": "yüksek"},
    "van": {"_default": "yüksek"},
    "diyarbakır": {"_default": "orta", "lice": "yüksek", "hani": "yüksek", "çermik": "yüksek"},
    "trabzon": {"_default": "düşük", "of": "orta", "hayrat": "orta"},
    "samsun": {"_default": "orta", "ladik": "yüksek", "havza": "yüksek", "vezirköprü": "yüksek", "kavak": "yüksek",
               "bafra": "düşük", "alaçam": "düşük"},
    "kocaeli": {"_default": "yüksek", "kandıra": "orta"},
    "sakarya": {"_default": "yüksek"},
    "yalova": {"_default": "yüksek"},
    "bursa": {"_default": "yüksek", "büyükorhan": "orta", "harmancık": "orta", "keles": "orta"},
    "tekirdağ": {"_default": "yüksek", "saray": "düşük", "kapaklı": "orta"},
    "balıkesir": {"_default": "yüksek", "kepsut": "orta", "dursunbey": "orta"},
    "çanakkale": {"_default": "yüksek", "bozcaada": "orta"},
    "edirne": {"_default": "düşük", "enez": "orta", "ipsala": "orta"},
    "kırklareli": {"_default": "düşük"},
    "denizli": {"_default": "yüksek"},
    "uşak": {"_default": "orta"},
    "kütahya": {"_default": "yüksek"},
    "afyonkarahisar": {"_default": "orta", "dinar": "yüksek", "çay": "yüksek", "sultandağı": "yüksek"},
    "eskişehir": {"_default": "orta", "inönü": "yüksek"},
    "konya": {"_default": "düşük", "akşehir": "yüksek", "tuzlukçu": "yüksek", "ılgın": "orta", "doğanhisar": "orta"},
    "kayseri": {"_default": "orta", "yahyalı": "orta", "sarız": "orta"},
    "sivas": {"_default": "orta", "suşehri": "yüksek", "koyulhisar": "yüksek", "gölova": "yüksek",
              "akıncılar": "yüksek", "divriği": "düşük"},
    "aksaray": {"_default": "düşük"},
    "karaman": {"_default": "düşük"},
    "niğde": {"_default": "orta", "bor": "orta"},
    "çankırı": {"_default": "yüksek", "yapraklı": "orta"},
    "kırşehir": {"_default": "orta"},
    "yozgat": {"_default": "orta", "akdağmadeni": "düşük"},
    "mersin": {"_default": "düşük", "tarsus": "orta", "çamlıyayla": "orta"},
    "osmaniye": {"_default": "yüksek"},
    "burdur": {"_default": "yüksek"},
    "isparta": {"_default": "yüksek"},
    "bolu": {"_default": "yüksek", "seben": "orta", "kıbrıscık": "orta"},
    "düzce": {"_default": "yüksek"},
    "zonguldak": {"_default": "düşük", "devrek": "yüksek", "gökçebey": "yüksek"},
    "bartın": {"_default": "düşük", "ulus": "orta"},
    "kastamonu": {"_default": "orta", "tosya": "yüksek", "cide": "düşük"},
    "sinop": {"_default": "düşük", "boyabat": "yüksek", "durağan": "yüksek"},
    "ordu": {"_default": "düşük", "mesudiye": "yüksek", "akkuş": "yüksek"},
    "giresun": {"_default": "düşük", "alucra": "yüksek", "şebinkarahisar": "yüksek", "çamoluk": "yüksek"},
    "rize": {"_default": "düşük"},
    "artvin": {"_default": "düşük", "yusufeli": "orta"},
    "tokat": {"_default": "yüksek", "artova": "orta"},
    "amasya": {"_default": "yüksek"},
    "çorum": {"_default": "orta", "osmancık": "yüksek", "kargı": "yüksek", "mecitözü": "yüksek"},
    "tunceli": {"_default": "yüksek", "pülümür": "yüksek"},
    "elazığ": {"_default": "yüksek"},
    "malatya": {"_default": "yüksek"},
    "adıyaman": {"_default": "yüksek"},
    "şanlıurfa": {"_default": "düşük", "bozova": "orta"},
    "mardin": {"_default": "düşük"},
    "batman": {"_default": "orta", "sason": "yüksek"},
    "siirt": {"_default": "yüksek"},
    "hakkari": {"_default": "yüksek"},
    "muş": {"_default": "yüksek"},
    "bitlis": {"_default": "yüksek"},
    "ağrı": {"_default": "orta", "patnos": "yüksek", "doğubayazıt": "yüksek"},
    "erzurum": {"_default": "yüksek", "ispir": "orta"},
    "kars": {"_default": "orta", "kağızman": "yüksek"},
    "ığdır": {"_default": "yüksek"},
    "ardahan": {"_default": "orta", "göle": "yüksek"}
}

ZEMIN_SINIF_MAP_RAW = {
    "istanbul": {"_default": "Z3", "arnavutköy": "Z2", "sarıyer": "Z1", "avcılar": "Z4", "bakırköy": "Z4"},
    "ankara": {"_default": "Z2", "etimesgut": "Z4", "gölbaşı": "Z4"},
    "izmir": {"_default": "Z3", "bayraklı": "Z4", "karşıyaka": "Z4"},
}


# -------------------------------------------------
#  HARİTA NORMALİZASYONU (Startup)
# -------------------------------------------------
def normalize_map_keys(raw_map: Dict) -> Dict:
    normalized = {}
    for il, il_data in raw_map.items():
        norm_il = normalize_key(il)
        normalized[norm_il] = {}
        for ilce, val in il_data.items():
            normalized[norm_il][normalize_key(ilce)] = val
    return normalized


DEPREM_RISK_MAP = normalize_map_keys(DEPREM_RISK_MAP_RAW)
ZEMIN_SINIF_MAP = normalize_map_keys(ZEMIN_SINIF_MAP_RAW)


def deprem_seviyesi_bul(il: str, ilce: str) -> str:
    il_key = normalize_key(il)
    ilce_key = normalize_key(ilce)

    il_data = DEPREM_RISK_MAP.get(il_key)
    if not il_data:
        return "orta"
    return il_data.get(ilce_key, il_data.get("_default", "orta"))


def deprem_seviyesi_puan(seviye: str) -> int:
    if seviye == "yüksek": return 3
    if seviye == "orta": return 1
    return 0


def tahmini_zemin_sinifi(il: str, ilce: str) -> str:
    il_key = normalize_key(il)
    ilce_key = normalize_key(ilce)
    il_data = ZEMIN_SINIF_MAP.get(il_key)
    if not il_data:
        return "Z3"
    return il_data.get(ilce_key, il_data.get("_default", "Z3"))


def yapisal_skor_hesapla(req: RiskRequest, zemin_sinifi: str) -> Tuple[int, List[str]]:
    skor = 0
    detaylar: List[str] = []

    if req.yapimYili <= 1975:
        skor += 5; detaylar.append(f"{req.yapimYili} ve öncesi (+5)")
    elif req.yapimYili <= 1999:
        skor += 4; detaylar.append(f"{req.yapimYili} – 1999 öncesi (+4)")
    elif req.yapimYili <= 2018:
        skor += 2; detaylar.append(f"{req.yapimYili} – 2018 öncesi (+2)")
    else:
        skor += 1; detaylar.append(f"{req.yapimYili} sonrası (+1)")

    if req.katSayisi <= 3:
        detaylar.append(f"{req.katSayisi} kat (+0)")
    elif req.katSayisi <= 5:
        skor += 1; detaylar.append(f"{req.katSayisi} kat (+1)")
    elif req.katSayisi <= 8:
        skor += 2; detaylar.append(f"{req.katSayisi} kat (+2)")
    else:
        skor += 4; detaylar.append(f"{req.katSayisi} kat (+4)")

    # --- YÖNETMELİK: Yüksek Yapı Kontrolü (TBDY 2018) ---
    # 21.50m üzeri (yaklaşık 7+ kat) = Yüksek Yapı → özel kurallar gerektirir
    if req.katSayisi >= 8:
        skor += 2
        detaylar.append(f"⚠️ Yüksek Yapı Kategorisi ({req.katSayisi} kat ≥ 8) - TBDY 2018 ek kurallar (+2)")

    if req.zeminDukkan == "evet": skor += 3; detaylar.append("Zemin katta dükkân (+3)")
    if req.bitisik == "evet": skor += 1; detaylar.append("Bitişik nizam (+1)")

    if req.hasar == "hafif":
        skor += 4; detaylar.append("Hafif hasar (+4)")
    elif req.hasar == "kolon":
        skor += 8; detaylar.append("Kolon hasarı (+8)")

    if req.kullanimAmaci in ["okul", "hastane"]: skor += 2; detaylar.append(
        f"Kritik kullanım ({req.kullanimAmaci}) (+2)")

    if req.kisaKolon == "var":
        skor += 3; detaylar.append("Kısa kolon (+3)")
    elif req.kisaKolon == "emin_degil":
        skor += 1; detaylar.append("Kısa kolon şüphesi (+1)")

    if req.agirCikma == "buyuk":
        skor += 2; detaylar.append("Büyük çıkma (+2)")
    elif req.agirCikma == "hafif":
        skor += 1; detaylar.append("Hafif çıkma (+1)")

    if req.planTipi in ["L", "T", "U"]:
        skor += 2; detaylar.append(f"Düzensiz plan {req.planTipi} (+2)")
    elif req.planTipi == "kompleks":
        skor += 3; detaylar.append("Kompleks plan (+3)")

    if req.bitisikHiza == "farkli": skor += 2; detaylar.append("Kat hizası farklı (+2)")

    cp = req.crackPuan
    if cp is not None and cp > 0:
        crack_skor_map = {0: 0, 1: 2, 2: 3, 3: 4}
        crack_skor = crack_skor_map.get(cp, 0)
        skor += crack_skor
        detaylar.append(f"Görsel çatlak analizi: Seviye {cp} (+{crack_skor})")

    if zemin_sinifi in ["Z3", "Z4"]:
        skor += 2; detaylar.append(f"Zayıf zemin {zemin_sinifi} (+2)")
    elif zemin_sinifi == "Z2":
        skor += 1; detaylar.append("Orta zemin Z2 (+1)")

    return skor, detaylar


def yapisal_seviye_etiketi(skor: int) -> str:
    if skor <= 5: return "Düşük"
    if skor <= 12: return "Orta"
    return "Yüksek"


# -------------------------------------------------
#  VERİ KAYDI (CSV) - LOCK İLE GÜVENLİ
# -------------------------------------------------
DATA_FILE = Path("veri_kayitlari.csv")
HEADER = ["tarih", "il", "ilce", "yapimYili", "katSayisi", "zeminDukkan", "bitisik", "hasar", "kullanimAmaci",
          "kisaKolon", "agirCikma", "planTipi", "bitisikHiza", "zeminSinifi", "crackPuan", "depremSeviye", "depremPuan",
          "yapisalPuan", "toplamYapisalRisk", "yapisalSeviye", "genelSeviye"]


def kayit_ekle_csv(data_list):
    try:
        with CSV_LOCK:
            yeni_dosya = not DATA_FILE.exists()
            with DATA_FILE.open("a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                if yeni_dosya: writer.writerow(HEADER)
                writer.writerow(data_list)
    except Exception as e:
        print(f"CSV Yazma Hatası: {e}")


# -------------------------------------------------
#  ANA ENDPOINT
# -------------------------------------------------
@app.get("/")
def root():
    return {"message": "Yapı Sağlığı Ön Tarama API çalışıyor (V12 Titanium)."}


@app.post("/api/risk-hesapla", response_model=RiskResponse)
def risk_hesapla(req: RiskRequest):
    # 1. Deprem ve Zemin Analizi
    deprem_seviye = deprem_seviyesi_bul(req.il, req.ilce)
    deprem_puan = deprem_seviyesi_puan(deprem_seviye)
    zemin_sinifi = req.zeminSinifi if req.zeminSinifi else tahmini_zemin_sinifi(req.il, req.ilce)

    # 2. Yapısal Skor
    yapisal_puan, detaylar = yapisal_skor_hesapla(req, zemin_sinifi)
    toplam_yapisal_risk = yapisal_puan + deprem_puan
    yapisal_seviye = yapisal_seviye_etiketi(toplam_yapisal_risk)

    # 3. Beton Dayanımı
    basinc_dayanimi = tahmin_beton_dayanimi(req.ultrasonikSesHizi, req.geriSicramaSayisi)
    if concrete_model is None:
        detaylar.append("UYARI: Beton modeli yok, varsayılan (C25) kullanıldı.")

    # --- YÖNETMELİK: Minimum Beton Sınıfı Kontrolü (TBDY 2018 Madde 7.2.5.3) ---
    # Deprem etkisi alacak elemanlarda en düşük beton sınıfı C25 (25 MPa) olmalıdır.
    if basinc_dayanimi < 25.0:
        detaylar.append(
            f"🚨 YÖNETMELİK UYARISI: Tahmini beton dayanımı ({basinc_dayanimi:.1f} MPa) "
            f"TBDY 2018 minimum sınırının (C25 = 25 MPa) altında! "
            f"Bu bina mevcut yönetmelik şartlarını karşılamıyor."
        )
        # Yapısal risk skoruna ciddi ceza ekle
        toplam_yapisal_risk += 5
        detaylar.append("Yönetmelik altı beton nedeniyle ek risk (+5)")

    # --- Korozyon Durum Etiketi (ASTM C876 standardına göre) ---
    if req.corrosion < -350:
        detaylar.append(f"Korozyon Durumu: YÜKSEK RİSK ({req.corrosion:.0f} mV < -350 mV)")
    elif req.corrosion < -200:
        detaylar.append(f"Korozyon Durumu: BELİRSİZ ({req.corrosion:.0f} mV, -350 ile -200 arası)")
    else:
        detaylar.append(f"Korozyon Durumu: Düşük Risk ({req.corrosion:.0f} mV > -200 mV)")

    # 4. Fuzzy Logic (Şeffaf Sınırlandırma ile)
    try:
        sim = ctrl.ControlSystemSimulation(fuzzy_control_system)

        # Clamp ve Uyarı Mekanizması
        f_strength = clamp(float(basinc_dayanimi), 0.0, 80.0)
        if f_strength != float(basinc_dayanimi):
            detaylar.append(
                f"NOT: Beton dayanımı fuzzy limitine sınırlandı ({basinc_dayanimi:.1f} -> {f_strength:.1f})")

        f_corrosion = clamp(float(req.corrosion), -600.0, 100.0)
        if f_corrosion != float(req.corrosion):
            detaylar.append(f"NOT: Korozyon fuzzy limitine sınırlandı ({req.corrosion:.0f} -> {f_corrosion:.0f})")

        f_survey = clamp(float(toplam_yapisal_risk), 0.0, 50.0)
        if f_survey != float(toplam_yapisal_risk):
            detaylar.append(f"NOT: Yapısal risk fuzzy limitine sınırlandı ({toplam_yapisal_risk} -> {f_survey})")

        sim.input['strength'] = f_strength
        sim.input['corrosion'] = f_corrosion
        sim.input['survey_risk'] = f_survey

        sim.compute()
        health_score = sim.output['health']
    except Exception as e:
        print(f"Fuzzy hesaplama hatası: {e}")
        health_score = 50.0

    # 5. Sonuç Hazırlığı
    health_score = clamp(health_score, 0.0, 100.0)
    fuzzy_label = get_fuzzy_label(health_score)

    if health_score < 45:
        genel_seviye = "Yüksek"
    elif health_score < 65:
        genel_seviye = "Orta"
    else:
        genel_seviye = "Düşük"

    # --- AI YORUM (BURASI DÜZELTİLDİ: Sola yaslandı) ---
    aciklama = get_llm_comment(
        skor=int(health_score),
        risk_durumu=fuzzy_label,
        beton=round(basinc_dayanimi, 1),
        korozyon=req.corrosion,
        risk_puani=int(toplam_yapisal_risk)
    )

    # Kayıt
    kayit_ekle_csv([
        datetime.now().isoformat(timespec="seconds"),
        req.il, req.ilce, req.yapimYili, req.katSayisi, req.zeminDukkan, req.bitisik, req.hasar,
        req.kullanimAmaci, req.kisaKolon, req.agirCikma, req.planTipi, req.bitisikHiza,
        zemin_sinifi, req.crackPuan if req.crackPuan is not None else 0,
        deprem_seviye, deprem_puan, yapisal_puan, toplam_yapisal_risk, yapisal_seviye, genel_seviye
    ])

    return RiskResponse(
        # İnsani Yuvarlama (Round)
        healthScore=int(round(health_score)),
        genelSeviye=genel_seviye,
        aciklama=aciklama,
        depremSeviye=deprem_seviye,
        depremPuan=deprem_puan,
        yapisalSeviye=yapisal_seviye,
        yapisalPuan=yapisal_puan,
        toplamYapisalRisk=toplam_yapisal_risk,
        zeminSinifi=zemin_sinifi,
        detaylar=detaylar,
        fuzzyLabel=fuzzy_label,
        corrosion=req.corrosion,
        basincDayanimi=basinc_dayanimi,
        aiEtiket=fuzzy_label,
        aiYorum=aciklama
    )
# V12 Titanium CI/CD Testi Başarılı!
if __name__ == "__main__":
    import uvicorn
    # CI/CD Testi: Bekçi burayı kontrol ediyor mu? (Test 1)
    uvicorn.run(app, host="127.0.0.1", port=8000)