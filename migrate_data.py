import os
import pandas as pd
from supabase import create_client, Client
from dotenv import load_dotenv
import pathlib

# .env dosyasını yükle
load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

if not url or not key:
    print("[HATA] .env dosyasinda SUPABASE_URL veya SUPABASE_KEY eksik!")
    exit(1)

supabase: Client = create_client(url, key)

CSV_FILE = "veri_kayitlari.csv"


def csv_to_supabase():
    if not pathlib.Path(CSV_FILE).exists():
        print(f"[HATA] {CSV_FILE} bulunamadi!")
        return

    print(f">> {CSV_FILE} okunuyor...")
    df = pd.read_csv(CSV_FILE)

    # NaN (boş) değerleri None'a çevir (SQL NULL için)
    df = df.where(pd.notnull(df), None)

    # Infinity veya -Infinity değerlerini temizle
    import numpy as np

    df = df.replace([np.inf, -np.inf], None)

    # Sütun isimlerini veritabanı şemasına uygun hale getir (camelCase -> snake_case)
    # CSV Header: tarih, il, ilce, yapimYili, katSayisi, zeminDukkan, bitisik, hasar, kullanimAmaci, kisaKolon, agirCikma, planTipi, bitisikHiza, zeminSinifi, crackPuan, depremSeviye, depremPuan, yapisalPuan, toplamYapisalRisk, yapisalSeviye, genelSeviye

    rename_map = {
        "tarih": "created_at",
        "il": "il",
        "ilce": "ilce",
        "yapimYili": "yapim_yili",
        "katSayisi": "kat_sayisi",
        "zeminDukkan": "zemin_dukkan",
        "bitisik": "bitisik_nizam",
        "hasar": "hasar_durumu",
        "kullanimAmaci": "kullanim_amaci",
        "kisaKolon": "kisa_kolon",
        "agirCikma": "agir_cikma",
        "planTipi": "plan_tipi",
        "bitisikHiza": "bitisik_hiza",
        "zeminSinifi": "zemin_sinifi",
        "crackPuan": "crack_puan",
        "depremSeviye": "deprem_seviye",
        "depremPuan": "deprem_puan",
        "yapisalPuan": "yapisal_puan",
        "toplamYapisalRisk": "toplam_risk_puani",
        "yapisalSeviye": "yapisal_seviye",
        "genelSeviye": "genel_seviye",
    }

    df = df.rename(columns=rename_map)

    # Sadece şemada tanımlı olan sütunları al
    TARGET_COLUMNS = list(rename_map.values())
    # DataFrame'de olup map'te olmayanları at
    existing_cols = [col for col in TARGET_COLUMNS if col in df.columns]
    df = df[existing_cols]

    # JSON Serializasyonu ile temizlik (En sağlam yöntem)
    # Pandas to_json, NaN ve Inf değerlerini otomatik olarak null yapar.
    # Sonra json.loads ile tekrar Python list/dict yapısına çeviririz.
    import json

    records = json.loads(df.to_json(orient="records", date_format="iso"))

    print(f"🚀 {len(records)} kayıt Supabase'e yükleniyor (batch: 50)...")

    batch_size = 50
    for i in range(0, len(records), batch_size):
        batch = records[i : i + batch_size]
        try:
            response = supabase.table("bina_analizleri").insert(batch).execute()
            print(f"[BASARILI] Batch {i//batch_size + 1} yuklendi ({len(batch)} kayit)")
        except Exception as e:
            error_msg = f"[HATA] Hata (Batch {i//batch_size + 1}):\n"
            if hasattr(e, "code"):
                error_msg += f"Code: {e.code}\n"
            if hasattr(e, "message"):
                error_msg += f"Message: {e.message}\n"
            if hasattr(e, "details"):
                error_msg += f"Details: {e.details}\n"
            if hasattr(e, "hint"):
                error_msg += f"Hint: {e.hint}\n"
            error_msg += f"Raw: {e}\n"

            print(error_msg)
            with open("migration_error.log", "w", encoding="utf-8") as f:
                f.write(error_msg)

            # Stop on first error to debug
            break


if __name__ == "__main__":
    csv_to_supabase()
