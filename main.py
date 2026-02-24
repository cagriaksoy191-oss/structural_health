from typing import List, Optional, Literal, Tuple, Dict
from pathlib import Path
from datetime import datetime
import csv
import time
import os

import pandas as pd
import joblib
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# --- Modüler İmportlar (Adım 1) ---
from config import supabase, CSV_LOCK
from models.schemas import RiskRequest, RiskResponse
from services.normalize import normalize_key


# -------------------------------------------------
#  FUZZY LOGIC & PREDICTION MODELLERİ (YAPISAL + BETON)
# -------------------------------------------------
def _parse_origins(raw: str) -> list:
    """ALLOWED_ORIGINS env var'ını virgülle ayırıp listeye çevirir."""
    return [o.strip() for o in raw.split(",") if o.strip()]


app = FastAPI(title="Yapı Sağlığı Ön Tarama API")

# --- CORS AYARLARI ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=_parse_origins(
        os.getenv(
            "ALLOWED_ORIGINS",
            "http://localhost:5173,http://localhost:5174,http://localhost:5175,http://127.0.0.1:5173",
        )
    ),
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Accept"],
)

# --- AI CONFIG (Qwen3) ---
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen3:8b"


# -------------------------------------------------
#  PYDANTIC MODELLERİ (Validasyonlu)
# RiskRequest, RiskResponse → models/schemas.py
# normalize_key → services/normalize.py
# (Backward-compat re-exportlar dosya sonundadır)


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
                    {"role": "user", "content": user_message},
                ],
                "stream": False,
                "options": {
                    "temperature": 0.7
                },  # Biraz yaratıcılık verelim ki konuşsun
            },
            timeout=120,
        )

        if response.status_code == 200:
            # Chat modunda cevap 'message' -> 'content' içindedir
            return response.json()["message"]["content"].strip()
        else:
            return f"⚠️ Bağlantı Hatası (Kod: {response.status_code}). Ollama açık mı?"

    except Exception as e:
        return f"⚠️ Yapay Zeka Cevap Vermedi: {str(e)}"


# -------------------------------------------------
#  FUZZY LOGIC SİSTEMİ
# -------------------------------------------------
def create_fuzzy_system():
    strength = ctrl.Antecedent(np.arange(0, 81, 1), "strength")
    corrosion = ctrl.Antecedent(np.arange(-600, 101, 1), "corrosion")
    survey_risk = ctrl.Antecedent(np.arange(0, 51, 1), "survey_risk")
    health = ctrl.Consequent(np.arange(0, 101, 1), "health")

    strength["low"] = fuzz.trapmf(strength.universe, [0, 0, 15, 25])
    strength["medium"] = fuzz.trimf(strength.universe, [20, 35, 50])
    strength["high"] = fuzz.trapmf(strength.universe, [40, 55, 80, 80])

    corrosion["high_risk"] = fuzz.trapmf(corrosion.universe, [-600, -600, -400, -300])
    corrosion["medium_risk"] = fuzz.trimf(corrosion.universe, [-400, -275, -150])
    corrosion["low_risk"] = fuzz.trapmf(corrosion.universe, [-200, -100, 100, 100])

    survey_risk["safe"] = fuzz.trapmf(survey_risk.universe, [0, 0, 10, 15])
    survey_risk["medium"] = fuzz.trimf(survey_risk.universe, [12, 25, 38])
    survey_risk["high"] = fuzz.trapmf(survey_risk.universe, [30, 40, 50, 50])

    health["very_bad"] = fuzz.trimf(health.universe, [0, 0, 25])
    health["bad"] = fuzz.trimf(health.universe, [20, 35, 50])
    health["medium"] = fuzz.trimf(health.universe, [45, 55, 65])
    health["good"] = fuzz.trimf(health.universe, [60, 75, 90])
    health["very_good"] = fuzz.trimf(health.universe, [80, 100, 100])

    # Kurallar
    rule_very_bad = ctrl.Rule(
        (corrosion["high_risk"])
        | (strength["low"] & survey_risk["high"])
        | (strength["low"] & corrosion["medium_risk"]),
        health["very_bad"],
    )
    rule_bad = ctrl.Rule(
        (strength["low"] & survey_risk["medium"] & corrosion["low_risk"])
        | (strength["medium"] & survey_risk["high"] & corrosion["low_risk"])
        | (corrosion["medium_risk"] & strength["medium"]),
        health["bad"],
    )
    rule_medium = ctrl.Rule(
        (strength["medium"] & survey_risk["medium"] & corrosion["low_risk"])
        | (strength["high"] & survey_risk["high"] & corrosion["low_risk"])
        | (corrosion["medium_risk"] & strength["high"]),
        health["medium"],
    )
    rule_good = ctrl.Rule(
        (strength["high"] & survey_risk["medium"] & corrosion["low_risk"])
        | (strength["medium"] & survey_risk["safe"] & corrosion["low_risk"]),
        health["good"],
    )
    rule_very_good = ctrl.Rule(
        (strength["high"] & survey_risk["safe"] & corrosion["low_risk"]),
        health["very_good"],
    )

    return ctrl.ControlSystem(
        [rule_very_bad, rule_bad, rule_medium, rule_good, rule_very_good]
    )


fuzzy_control_system = create_fuzzy_system()


def get_fuzzy_label(score: float) -> str:
    if score < 25:
        return "Very Bad (Çok Kötü - Acil)"
    if score < 45:
        return "Bad (Kötü - Güçlendirme Gerekli)"
    if score < 65:
        return "Medium (Orta Risk - İnceleme Gerekli)"
    if score < 85:
        return "Good (İyi - Bakım Önerilir)"
    return "Very Good (Çok İyi - Sağlam)"


def clamp(val: float, low: float, high: float) -> float:
    return max(low, min(high, val))


def korozyon_olasiligi(mv: float) -> tuple:
    """
    ASTM C876 standardına göre korozyon olasılığını yüzde olarak hesaplar.
    Sürekli (continuous) interpolasyon ile hassas sonuç verir.

    Referans eşikler:
      > -200 mV  → %90+ korozyon YOK
      -200 ~ -350 mV → Belirsiz bölge (lineer interpolasyon)
      < -350 mV  → %90+ korozyon VAR

    Returns: (yuzde: int, seviye: str, renk_kodu: str)
    """
    if mv >= -100:
        yuzde = 5
    elif mv >= -200:
        # -100 → %5,  -200 → %10  (güvenli bölge)
        yuzde = int(5 + ((-100 - mv) / 100) * 5)
    elif mv >= -350:
        # -200 → %10,  -350 → %90  (belirsiz bölge, lineer artış)
        yuzde = int(10 + ((-200 - mv) / 150) * 80)
    elif mv >= -500:
        # -350 → %90,  -500 → %97  (yüksek risk bölgesi)
        yuzde = int(90 + ((-350 - mv) / 150) * 7)
    else:
        yuzde = 98

    yuzde = max(2, min(98, yuzde))  # %2-%98 aralığında tut

    if yuzde <= 15:
        return yuzde, "Düşük", "🟢"
    elif yuzde <= 40:
        return yuzde, "Orta-Düşük", "🟡"
    elif yuzde <= 65:
        return yuzde, "Orta", "🟠"
    elif yuzde <= 85:
        return yuzde, "Yüksek", "🔴"
    else:
        return yuzde, "Çok Yüksek", "🔴"


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

# -------------------------------------------------
#  RİSK MODELİ (RandomForest Classifier — Ensemble)
# -------------------------------------------------
RISK_MODEL_PATH = Path("risk_model.joblib")
risk_model = None
try:
    if RISK_MODEL_PATH.exists():
        risk_model = joblib.load(RISK_MODEL_PATH)
        print("✅ Risk Modeli (RandomForest) yüklendi.")
    else:
        print("⚠️ Risk Modeli bulunamadı. Fuzzy-only modda çalışılacak.")
except Exception as e:
    print(f"⚠️ Risk Modeli yükleme hatası: {e}")

RF_CLASS_SCORES = {"Düşük": 80, "Orta": 50, "Yüksek": 20}


def rf_health_score(req, zemin_sinifi: str, basinc_dayanimi: float):
    """RF predict_proba ile 0-100 sağlık skoru üretir. Hata olursa None döner."""
    if risk_model is None:
        return None
    try:
        input_df = pd.DataFrame(
            [
                {
                    "il": req.il,
                    "ilce": req.ilce or "",
                    "yapimYili": req.yapimYili,
                    "katSayisi": req.katSayisi,
                    "zeminDukkan": req.zeminDukkan,
                    "bitisik": req.bitisik,
                    "hasar": req.hasar,
                    "kullanimAmaci": req.kullanimAmaci,
                    "kisaKolon": req.kisaKolon,
                    "agirCikma": req.agirCikma,
                    "planTipi": req.planTipi,
                    "bitisikHiza": req.bitisikHiza or "yok",
                    "zeminSinifi": zemin_sinifi,
                    "ultrasonikSesHizi": req.ultrasonikSesHizi,
                    "geriSicramaSayisi": req.geriSicramaSayisi,
                    "basincDayanimi": basinc_dayanimi,
                }
            ]
        )
        probas = risk_model.predict_proba(input_df)[0]
        classes = risk_model.classes_
        return sum(p * RF_CLASS_SCORES.get(c, 50) for p, c in zip(probas, classes))
    except Exception as e:
        print(f"⚠️ RF tahmin hatası: {e}")
        return None


def tahmin_beton_dayanimi(upv: float, rn: float) -> float:
    if concrete_model is None:
        return 25.0
    try:
        res = concrete_model.predict(pd.DataFrame({"UPV": [upv], "RN": [rn]}))[0]
        return float(res)
    except:
        return 25.0


# -------------------------------------------------
#  HARİTA VERİLERİ (RAW)
# -------------------------------------------------
DEPREM_RISK_MAP_RAW = {
    "istanbul": {
        "_default": "yüksek",
        "arnavutköy": "düşük",
        "sarıyer": "orta",
        "eyüpsultan": "orta",
        "beykoz": "düşük",
        "şile": "düşük",
        "çatalca": "orta",
        "başakşehir": "orta",
        "avcılar": "yüksek",
        "bakırköy": "yüksek",
        "küçükçekmece": "yüksek",
        "zeytinburnu": "yüksek",
        "fatih": "yüksek",
        "kadıköy": "yüksek",
        "maltepe": "yüksek",
        "kartal": "yüksek",
        "tuzla": "yüksek",
        "pendik": "yüksek",
        "adalar": "yüksek",
        "büyükçekmece": "yüksek",
        "silivri": "yüksek",
        "esenler": "orta",
        "sultangazi": "orta",
    },
    "ankara": {
        "_default": "düşük",
        "elmadağ": "orta",
        "nallıhan": "yüksek",
        "beypazarı": "orta",
        "kazan": "orta",
        "kızılcahamam": "yüksek",
        "çamlıdere": "yüksek",
        "evren": "orta",
        "bala": "orta",
    },
    "izmir": {
        "_default": "yüksek",
        "kiraz": "orta",
        "beydağ": "orta",
        "karaburun": "orta",
    },
    "manisa": {"_default": "yüksek", "demirci": "orta", "gördes": "orta"},
    "aydın": {"_default": "yüksek"},
    "muğla": {"_default": "yüksek", "datça": "orta"},
    "antalya": {
        "_default": "orta",
        "demre": "yüksek",
        "finike": "yüksek",
        "kumluca": "yüksek",
        "kemer": "yüksek",
        "kaş": "yüksek",
        "alanya": "düşük",
        "gündoğmuş": "düşük",
        "gazipaşa": "düşük",
    },
    "adana": {
        "_default": "yüksek",
        "tufanbeyli": "orta",
        "saimbeyli": "orta",
        "pozantı": "orta",
    },
    "hatay": {"_default": "yüksek"},
    "kahramanmaraş": {"_default": "yüksek", "ekinözü": "orta"},
    "erzincan": {"_default": "yüksek"},
    "bingöl": {"_default": "yüksek"},
    "van": {"_default": "yüksek"},
    "diyarbakır": {
        "_default": "orta",
        "lice": "yüksek",
        "hani": "yüksek",
        "çermik": "yüksek",
    },
    "trabzon": {"_default": "düşük", "of": "orta", "hayrat": "orta"},
    "samsun": {
        "_default": "orta",
        "ladik": "yüksek",
        "havza": "yüksek",
        "vezirköprü": "yüksek",
        "kavak": "yüksek",
        "bafra": "düşük",
        "alaçam": "düşük",
    },
    "kocaeli": {"_default": "yüksek", "kandıra": "orta"},
    "sakarya": {"_default": "yüksek"},
    "yalova": {"_default": "yüksek"},
    "bursa": {
        "_default": "yüksek",
        "büyükorhan": "orta",
        "harmancık": "orta",
        "keles": "orta",
    },
    "tekirdağ": {"_default": "yüksek", "saray": "düşük", "kapaklı": "orta"},
    "balıkesir": {"_default": "yüksek", "kepsut": "orta", "dursunbey": "orta"},
    "çanakkale": {"_default": "yüksek", "bozcaada": "orta"},
    "edirne": {"_default": "düşük", "enez": "orta", "ipsala": "orta"},
    "kırklareli": {"_default": "düşük"},
    "denizli": {"_default": "yüksek"},
    "uşak": {"_default": "orta"},
    "kütahya": {"_default": "yüksek"},
    "afyonkarahisar": {
        "_default": "orta",
        "dinar": "yüksek",
        "çay": "yüksek",
        "sultandağı": "yüksek",
    },
    "eskişehir": {"_default": "orta", "inönü": "yüksek"},
    "konya": {
        "_default": "düşük",
        "akşehir": "yüksek",
        "tuzlukçu": "yüksek",
        "ılgın": "orta",
        "doğanhisar": "orta",
    },
    "kayseri": {"_default": "orta", "yahyalı": "orta", "sarız": "orta"},
    "sivas": {
        "_default": "orta",
        "suşehri": "yüksek",
        "koyulhisar": "yüksek",
        "gölova": "yüksek",
        "akıncılar": "yüksek",
        "divriği": "düşük",
    },
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
    "giresun": {
        "_default": "düşük",
        "alucra": "yüksek",
        "şebinkarahisar": "yüksek",
        "çamoluk": "yüksek",
    },
    "rize": {"_default": "düşük"},
    "artvin": {"_default": "düşük", "yusufeli": "orta"},
    "tokat": {"_default": "yüksek", "artova": "orta"},
    "amasya": {"_default": "yüksek"},
    "çorum": {
        "_default": "orta",
        "osmancık": "yüksek",
        "kargı": "yüksek",
        "mecitözü": "yüksek",
    },
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
    "ardahan": {"_default": "orta", "göle": "yüksek"},
}

ZEMIN_SINIF_MAP_RAW = {
    "istanbul": {
        "_default": "Z3",
        "arnavutköy": "Z2",
        "sarıyer": "Z1",
        "avcılar": "Z4",
        "bakırköy": "Z4",
    },
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
    if seviye == "yüksek":
        return 3
    if seviye == "orta":
        return 1
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
        skor += 5
        detaylar.append(f"{req.yapimYili} ve öncesi (+5)")
    elif req.yapimYili <= 1999:
        skor += 4
        detaylar.append(f"{req.yapimYili} – 1999 öncesi (+4)")
    elif req.yapimYili <= 2018:
        skor += 2
        detaylar.append(f"{req.yapimYili} – 2018 öncesi (+2)")
    else:
        skor += 1
        detaylar.append(f"{req.yapimYili} sonrası (+1)")

    if req.katSayisi <= 3:
        detaylar.append(f"{req.katSayisi} kat (+0)")
    elif req.katSayisi <= 5:
        skor += 1
        detaylar.append(f"{req.katSayisi} kat (+1)")
    elif req.katSayisi <= 8:
        skor += 2
        detaylar.append(f"{req.katSayisi} kat (+2)")
    else:
        skor += 4
        detaylar.append(f"{req.katSayisi} kat (+4)")

    # --- YÖNETMELİK: Yüksek Yapı Kontrolü (TBDY 2018) ---
    # 21.50m üzeri (yaklaşık 7+ kat) = Yüksek Yapı → özel kurallar gerektirir
    if req.katSayisi >= 8:
        skor += 2
        detaylar.append(
            f"⚠️ Yüksek Yapı Kategorisi ({req.katSayisi} kat ≥ 8) - TBDY 2018 ek kurallar (+2)"
        )

    if req.zeminDukkan == "evet":
        skor += 3
        detaylar.append("Zemin katta dükkân (+3)")
    if req.bitisik == "evet":
        skor += 1
        detaylar.append("Bitişik nizam (+1)")

    if req.hasar == "hafif":
        skor += 4
        detaylar.append("Hafif hasar (+4)")
    elif req.hasar == "kolon":
        skor += 8
        detaylar.append("Kolon hasarı (+8)")

    if req.kullanimAmaci in ["okul", "hastane"]:
        skor += 2
        detaylar.append(f"Kritik kullanım ({req.kullanimAmaci}) (+2)")

    if req.kisaKolon == "var":
        skor += 3
        detaylar.append("Kısa kolon (+3)")
    elif req.kisaKolon == "emin_degil":
        skor += 1
        detaylar.append("Kısa kolon şüphesi (+1)")

    if req.agirCikma == "buyuk":
        skor += 2
        detaylar.append("Büyük çıkma (+2)")
    elif req.agirCikma == "hafif":
        skor += 1
        detaylar.append("Hafif çıkma (+1)")

    if req.planTipi in ["L", "T", "U"]:
        skor += 2
        detaylar.append(f"Düzensiz plan {req.planTipi} (+2)")
    elif req.planTipi == "kompleks":
        skor += 3
        detaylar.append("Kompleks plan (+3)")

    if req.bitisikHiza == "farkli":
        skor += 2
        detaylar.append("Kat hizası farklı (+2)")

    cp = req.crackPuan
    if cp is not None and cp > 0:
        crack_skor_map = {0: 0, 1: 2, 2: 3, 3: 4}
        crack_skor = crack_skor_map.get(cp, 0)
        skor += crack_skor
        detaylar.append(f"Görsel çatlak analizi: Seviye {cp} (+{crack_skor})")

    if zemin_sinifi in ["Z3", "Z4"]:
        skor += 2
        detaylar.append(f"Zayıf zemin {zemin_sinifi} (+2)")
    elif zemin_sinifi == "Z2":
        skor += 1
        detaylar.append("Orta zemin Z2 (+1)")

    return skor, detaylar


def yapisal_seviye_etiketi(skor: int) -> str:
    if skor <= 5:
        return "Düşük"
    if skor <= 12:
        return "Orta"
    return "Yüksek"


# -------------------------------------------------
#  VERİ KAYDI (CSV) - LOCK İLE GÜVENLİ
# -------------------------------------------------
DATA_FILE = Path("veri_kayitlari.csv")
HEADER = [
    "tarih",
    "il",
    "ilce",
    "yapimYili",
    "katSayisi",
    "zeminDukkan",
    "bitisik",
    "hasar",
    "kullanimAmaci",
    "kisaKolon",
    "agirCikma",
    "planTipi",
    "bitisikHiza",
    "zeminSinifi",
    "crackPuan",
    "depremSeviye",
    "depremPuan",
    "yapisalPuan",
    "toplamYapisalRisk",
    "yapisalSeviye",
    "genelSeviye",
]


def kayit_ekle_supabase(record_dict: dict):
    """
    Veriyi Supabase 'bina_analizleri' tablosuna ekler.
    Bağlantı yoksa veya hata olursa konsola yazar (Prod: Kuyruğa atılmalı).
    """
    if not supabase:
        print("❌ Supabase istemcisi yüklü değil! Kayıt atlandı.")
        return

    try:
        # Arka planda (async değil ama hızlı) gönderim
        # .execute() sonucu bekler.
        response = supabase.table("bina_analizleri").insert(record_dict).execute()
        # print(f"✅ Supabase Kayıt Başarılı: {response}")
    except Exception as e:
        print(f"❌ Supabase Yazma Hatası: {e}")


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
    zemin_sinifi = (
        req.zeminSinifi if req.zeminSinifi else tahmini_zemin_sinifi(req.il, req.ilce)
    )

    # 2. Yapısal Skor
    yapisal_puan, detaylar = yapisal_skor_hesapla(req, zemin_sinifi)
    toplam_yapisal_risk = yapisal_puan + deprem_puan
    yapisal_seviye = yapisal_seviye_etiketi(toplam_yapisal_risk)

    # 3. Beton Dayanımı
    basinc_dayanimi = tahmin_beton_dayanimi(
        req.ultrasonikSesHizi, req.geriSicramaSayisi
    )
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

    # --- Korozyon Olasılığı (ASTM C876 standardı, sürekli interpolasyon) ---
    kor_yuzde, kor_seviye, kor_ikon = korozyon_olasiligi(req.corrosion)
    detaylar.append(
        f"{kor_ikon} Korozyon Olasılığı: %{kor_yuzde} ({kor_seviye}) "
        f"[{req.corrosion:.0f} mV — ASTM C876]"
    )

    # 4. Fuzzy Logic (Şeffaf Sınırlandırma ile)
    try:
        sim = ctrl.ControlSystemSimulation(fuzzy_control_system)

        # Clamp ve Uyarı Mekanizması
        f_strength = clamp(float(basinc_dayanimi), 0.0, 80.0)
        if f_strength != float(basinc_dayanimi):
            detaylar.append(
                f"NOT: Beton dayanımı fuzzy limitine sınırlandı ({basinc_dayanimi:.1f} -> {f_strength:.1f})"
            )

        f_corrosion = clamp(float(req.corrosion), -600.0, 100.0)
        if f_corrosion != float(req.corrosion):
            detaylar.append(
                f"NOT: Korozyon fuzzy limitine sınırlandı ({req.corrosion:.0f} -> {f_corrosion:.0f})"
            )

        f_survey = clamp(float(toplam_yapisal_risk), 0.0, 50.0)
        if f_survey != float(toplam_yapisal_risk):
            detaylar.append(
                f"NOT: Yapısal risk fuzzy limitine sınırlandı ({toplam_yapisal_risk} -> {f_survey})"
            )

        sim.input["strength"] = f_strength
        sim.input["corrosion"] = f_corrosion
        sim.input["survey_risk"] = f_survey

        sim.compute()
        health_score = sim.output["health"]
    except Exception as e:
        print(f"Fuzzy hesaplama hatası: {e}")
        health_score = 50.0

    # 5. Ensemble: Fuzzy + RF (predict_proba tabanlı)
    fuzzy_raw = clamp(health_score, 0.0, 100.0)
    rf_score = rf_health_score(req, zemin_sinifi, basinc_dayanimi)
    if rf_score is not None:
        health_score = 0.6 * fuzzy_raw + 0.4 * rf_score
        detaylar.append(
            f"🤖 Ensemble: Fuzzy({fuzzy_raw:.0f}) + RF({rf_score:.0f}) → {health_score:.0f}"
        )
    else:
        health_score = fuzzy_raw
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
        risk_puani=int(toplam_yapisal_risk),
    )

    # Kayıt (Supabase)
    kayit_ekle_supabase(
        {
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "il": req.il,
            "ilce": req.ilce,
            "yapim_yili": req.yapimYili,
            "kat_sayisi": req.katSayisi,
            "zemin_dukkan": req.zeminDukkan,
            "bitisik_nizam": req.bitisik,
            "hasar_durumu": req.hasar,
            "kullanim_amaci": req.kullanimAmaci,
            "kisa_kolon": req.kisaKolon,
            "agir_cikma": req.agirCikma,
            "plan_tipi": req.planTipi,
            "bitisik_hiza": req.bitisikHiza,
            "zemin_sinifi": zemin_sinifi,
            "crack_puan": req.crackPuan if req.crackPuan is not None else 0,
            "deprem_seviye": deprem_seviye,
            "deprem_puan": deprem_puan,
            "yapisal_puan": yapisal_puan,
            "toplam_risk_puani": toplam_yapisal_risk,
            "yapisal_seviye": yapisal_seviye,
            "genel_seviye": genel_seviye,
            "ai_etiket": fuzzy_label,
            "ai_yorum": aciklama,
        }
    )

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
        aiYorum=aciklama,
    )


# V12 Titanium CI/CD Testi Başarılı!
if __name__ == "__main__":
    import uvicorn

    # CI/CD Testi: Bekçi burayı kontrol ediyor mu? (Test 1)
    uvicorn.run(app, host="127.0.0.1", port=8000)
