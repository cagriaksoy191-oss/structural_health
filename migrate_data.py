import os
import asyncio
import pandas as pd
from supabase import create_async_client, AsyncClient
from dotenv import load_dotenv
import pathlib
import json
import numpy as np

# .env dosyasını yükle
load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

if not url or not key:
    print("[HATA] .env dosyasinda SUPABASE_URL veya SUPABASE_KEY eksik!")
    exit(1)

CSV_FILE = "veri_kayitlari.csv"


async def insert_batch(
    supabase: AsyncClient, batch: list, batch_idx: int, semaphore: asyncio.Semaphore
):
    """Bir batch veriyi asenkron olarak Supabase'e yükler."""
    async with semaphore:
        try:
            # .execute() asenkron client kullanıldığında await edilmelidir
            await supabase.table("bina_analizleri").insert(batch).execute()
            print(f"[BASARILI] Batch {batch_idx + 1} yuklendi ({len(batch)} kayit)")
        except Exception as e:
            error_msg = f"[HATA] Hata (Batch {batch_idx + 1}): {type(e).__name__}\n"
            print(error_msg)
            with open("migration_error.log", "a", encoding="utf-8") as f:
                f.write(error_msg)
            raise e


async def csv_to_supabase():
    if not pathlib.Path(CSV_FILE).exists():
        print(f"[HATA] {CSV_FILE} bulunamadi!")
        return

    print(f">> {CSV_FILE} okunuyor...")
    df = pd.read_csv(CSV_FILE)

    # NaN (boş) değerleri None'a çevir (SQL NULL için)
    df = df.where(pd.notnull(df), None)

    # Infinity veya -Infinity değerlerini temizle
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
    records = json.loads(df.to_json(orient="records", date_format="iso"))

    print(f"🚀 {len(records)} kayıt Supabase'e yükleniyor (batch: 50, async)...")

    # Async client oluştur
    supabase: AsyncClient = create_async_client(url, key)

    batch_size = 50
    # Eşzamanlılık sınırı (Aynı anda en fazla 5 istek)
    semaphore = asyncio.Semaphore(5)

    tasks = []
    for i in range(0, len(records), batch_size):
        batch = records[i : i + batch_size]
        tasks.append(insert_batch(supabase, batch, i // batch_size, semaphore))

    if not tasks:
        print("Yüklenecek kayıt bulunamadı.")
        return

    try:
        await asyncio.gather(*tasks)
        print(f"\n[TAMAMLANDI] {len(records)} kayıt başarıyla aktarıldı.")
    except Exception:
        print("\n[DURDURULDU] Bir veya daha fazla batch yüklenirken hata oluştu.")


if __name__ == "__main__":
    try:
        asyncio.run(csv_to_supabase())
    except KeyboardInterrupt:
        print("\nİşlem kullanıcı tarafından durduruldu.")
