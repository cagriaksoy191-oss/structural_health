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

