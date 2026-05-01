"""Yapı Sağlığı — Konfigürasyon ve Bağlantılar"""

import os
import threading
from typing import Optional

from dotenv import load_dotenv
from supabase import create_client, Client

# .env dosyasını yükle
load_dotenv()

# Supabase Ayarları
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Optional[Client] = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("[BASARILI] Supabase baglantisi kuruldu.")
    except Exception as e:
        print(f"[HATA] Supabase baglanti hatasi: {type(e).__name__}")
else:
    print(
        "[UYARI] SUPABASE_URL veya SUPABASE_KEY eksik! Veriler sadece CSV'ye yazilabilir (yedek mod)."
    )

# --- CSV THREAD LOCK ---
# Not: Sunum sırasında (tek worker) bu kilit dosyayı korur.
CSV_LOCK = threading.Lock()

# --- AFAD Deprem API Ayarları ---
AFAD_API_BASE_URL = "https://deprem.afad.gov.tr/apiv2/event/filter"
AFAD_TIMEOUT = int(os.getenv("AFAD_TIMEOUT", "10"))  # saniye (HTTP timeout)
AFAD_CACHE_TTL = int(os.getenv("AFAD_CACHE_TTL", "3600"))  # saniye (varsayılan 1 saat)
