"""Yapı Sağlığı — CSV ve Supabase Veri Kayıt"""

import csv
from pathlib import Path

from config import supabase, CSV_LOCK


# -------------------------------------------------
#  VERİ KAYDI (CSV) - LOCK İLE GÜVENLİ
# -------------------------------------------------
DATA_FILE = Path("veri_kayitlari.csv")

# Supabase record_dict snake_case anahtarlarıyla birebir hizalı
HEADER = [
    "created_at",
    "il",
    "ilce",
    "yapim_yili",
    "kat_sayisi",
    "zemin_dukkan",
    "bitisik_nizam",
    "hasar_durumu",
    "kullanim_amaci",
    "kisa_kolon",
    "agir_cikma",
    "plan_tipi",
    "bitisik_hiza",
    "zemin_sinifi",
    "crack_puan",
    "deprem_seviye",
    "deprem_puan",
    "yapisal_puan",
    "toplam_risk_puani",
    "yapisal_seviye",
    "genel_seviye",
    "ai_etiket",
    "ai_yorum",
    "engine_version",
]


def kayit_ekle_csv(record_dict: dict):
    """
    Veriyi CSV dosyasına HEADER sırasıyla yazar.
    Thread-safe: CSV_LOCK ile korunur.
    record_dict Supabase ile aynı dict olmalı.
    """
    try:
        with CSV_LOCK:
            file_exists = DATA_FILE.exists() and DATA_FILE.stat().st_size > 0
            with open(DATA_FILE, "a", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=HEADER, extrasaction="ignore")
                if not file_exists:
                    writer.writeheader()
                writer.writerow(record_dict)
    except Exception as e:
        print(f"[HATA] CSV Yazma Hatasi: {e}")


def kayit_ekle_supabase(record_dict: dict):
    """
    Veriyi Supabase 'bina_analizleri' tablosuna ekler.
    Bağlantı yoksa veya hata olursa konsola yazar (Prod: Kuyruğa atılmalı).
    """
    if not supabase:
        print("[HATA] Supabase istemcisi yuklu degil! Kayit atlandi.")
        return

    try:
        # Arka planda (async değil ama hızlı) gönderim
        # .execute() sonucu bekler.
        response = supabase.table("bina_analizleri").insert(record_dict).execute()
        # print(f"[BASARILI] Supabase Kayit Basarili: {response}")
    except Exception as e:
        print(f"[HATA] Supabase Yazma Hatasi: {e}")
