"""Yapı Sağlığı Ön Tarama API — Ana Giriş Noktası"""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# statik dosyalar için dizin oluştur (PDF vs.)
if not os.path.exists("static"):
    os.makedirs("static")

# --- Route İmport ---
from routes.risk import router as risk_router


# -------------------------------------------------
#  FASTAPI APP & CORS
# -------------------------------------------------
def _parse_origins(raw: str) -> list:
    """ALLOWED_ORIGINS env var'ını virgülle ayırıp listeye çevirir."""
    return [o.strip() for o in raw.split(",") if o.strip()]


app = FastAPI(title="Yapı Sağlığı Ön Tarama API")

# --- STATIC FILES ---
app.mount("/static", StaticFiles(directory="static"), name="static")

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

# --- Route Kayıt ---
app.include_router(risk_router)


@app.get("/")
def root():
    return {"message": "Yapı Sağlığı Ön Tarama API çalışıyor (V12 Titanium)."}


# ============================================================
# BACKWARD COMPAT: Eski importları kırmamak için re-export
# "from main import RiskRequest" vb. hâlâ çalışır
# ============================================================
from config import supabase, CSV_LOCK  # noqa: E402, F401
from models.schemas import RiskRequest, RiskResponse  # noqa: E402, F401
from services.normalize import normalize_key  # noqa: E402, F401
from services.fuzzy_engine import (
    fuzzy_control_system,
    get_fuzzy_label,
    clamp,
)  # noqa: E402, F401
from services.corrosion import korozyon_olasiligi  # noqa: E402, F401
from services.ml_models import (
    concrete_model,
    rf_health_score,
    tahmin_beton_dayanimi,
)  # noqa: E402, F401
from services.earthquake import (
    deprem_seviyesi_bul,
    deprem_seviyesi_puan,
    tahmini_zemin_sinifi,
)  # noqa: E402, F401
from services.structural import (
    yapisal_skor_hesapla,
    yapisal_seviye_etiketi,
)  # noqa: E402, F401
from services.ai_comment import get_llm_comment  # noqa: E402, F401
from services.data_service import kayit_ekle_supabase  # noqa: E402, F401
from routes.risk import risk_hesapla  # noqa: E402, F401


# V12 Titanium CI/CD Testi Başarılı!
if __name__ == "__main__":
    import uvicorn

    # CI/CD Testi: Bekçi burayı kontrol ediyor mu? (Test 1)
    uvicorn.run(app, host="127.0.0.1", port=8000)
