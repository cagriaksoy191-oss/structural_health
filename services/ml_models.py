"""Yapı Sağlığı — ML Model Yükleme ve Tahmin"""

import logging

from pathlib import Path

import pandas as pd
import joblib


# -------------------------------------------------
#  BETON MODELİ
# -------------------------------------------------
CONCRETE_MODEL_PATH = Path("concrete_model.joblib")
concrete_model = None
try:
    if CONCRETE_MODEL_PATH.exists():
        concrete_model = joblib.load(CONCRETE_MODEL_PATH)
        print("[BASARILI] Beton Modeli (RandomForest) yüklendi.")
    else:
        print("[UYARI] Beton Modeli bulunamadı.")
except Exception as e:
    print(f"Model yükleme hatası: {e}")

# -------------------------------------------------
#  RİSK MODELİ (RandomForest Classifier)
#  DEPRECATED: v2_fuzzy27'de karar üretiminde kullanılmıyor.
#  Backward-compat geçiş süresi için korunuyor.
# -------------------------------------------------
RISK_MODEL_PATH = Path("risk_model.joblib")
risk_model = None
try:
    if RISK_MODEL_PATH.exists():
        risk_model = joblib.load(RISK_MODEL_PATH)
        print("[BASARILI] Risk Modeli (RandomForest) yüklendi.")
    else:
        print("[UYARI] Risk Modeli bulunamadı. Fuzzy-only modda çalışılacak.")
except Exception as e:
    print(f"[UYARI] Risk Modeli yükleme hatası: {e}")

RF_CLASS_SCORES = {"Düşük": 80, "Orta": 50, "Yüksek": 20}


def rf_health_score(req, zemin_sinifi: str, basinc_dayanimi: float):
    """DEPRECATED: v2_fuzzy27'de kullanılmıyor. RF predict_proba ile 0-100 sağlık skoru üretir."""
    import warnings
    warnings.warn(
        "rf_health_score() v2_fuzzy27'de kullanılmıyor. Karar motoru Fuzzy + Policy Layer.",
        DeprecationWarning,
        stacklevel=2,
    )
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
        print(f"[UYARI] RF tahmin hatası: {e}")
        return None


logger = logging.getLogger(__name__)


def tahmin_beton_dayanimi(upv: float, rn: float) -> tuple[float, bool]:
    """Beton basınç dayanımı tahmini.

    Returns:
        (mpa_value, used_fallback) — fallback True ise 25.0 MPa varsayılan kullanıldı.
    """
    if concrete_model is None:
        return 25.0, True
    try:
        res = concrete_model.predict(pd.DataFrame({"UPV": [upv], "RN": [rn]}))[0]
        return float(res), False
    except Exception as e:
        logger.warning("Beton predict hatasi: %s", e)
        return 25.0, True

