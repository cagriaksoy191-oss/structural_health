"""Yapı Sağlığı — CSV ve Supabase Veri Kayıt"""

import csv
from pathlib import Path

from config import supabase, CSV_LOCK


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
