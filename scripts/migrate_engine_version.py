"""Supabase Migration: engine_version kolonu ekleme — SQL Helper.

3 adımlı güvenli rollout stratejisi:
  1. Kolonu default olmadan ekle (mevcut satırlar etkilenmez)
  2. Legacy satırları backfill et
  3. Yeni satırlar için default ayarla

KULLANIM:
  Bu script SQL helper'dır — SQL'i ekrana yazdırır,
  kullanıcı Supabase Dashboard > SQL Editor'da çalıştırır.
  Otomatik DB bağlantısı YOKTUR.

  python scripts/migrate_engine_version.py --step 1      # Tek adım göster
  python scripts/migrate_engine_version.py --step all     # Tüm adımları göster
  python scripts/migrate_engine_version.py --step verify  # Doğrulama sorgusu

ROLLOUT SIRASI:
  1. --step 1 çalıştır → SQL'i kopyala → SQL Editor'da uygula
  2. --step verify çalıştır → SQL'i kopyala → satır sayılarını doğrula
  3. --step 2 çalıştır → SQL'i kopyala → SQL Editor'da uygula
  4. --step verify çalıştır → backfill sonucunu doğrula
  5. --step 3 çalıştır → SQL'i kopyala → SQL Editor'da uygula
  6. --step verify çalıştır → default'un çalıştığını doğrula
"""

# ======================================================================
#  SQL STATEMENTS
# ======================================================================

STEP_1_ADD_COLUMN = """
-- Adım 1: Kolonu nullable + default'suz ekle
-- Mevcut satırlar NULL olarak kalır, hizmet kesintisi yok
ALTER TABLE bina_analizleri
ADD COLUMN IF NOT EXISTS engine_version TEXT;
""".strip()

STEP_2_BACKFILL = """
-- Adım 2: Legacy satırları backfill et
-- NULL olan satırlar v1 ensemble ile üretilmişti
UPDATE bina_analizleri
SET engine_version = 'v1_ensemble'
WHERE engine_version IS NULL;
""".strip()

STEP_3_SET_DEFAULT = """
-- Adım 3: Yeni satırlar için default ayarla
-- Bundan sonra insert edilen her satır otomatik v2_fuzzy27 alır
ALTER TABLE bina_analizleri
ALTER COLUMN engine_version SET DEFAULT 'v2_fuzzy27';
""".strip()

VERIFY_QUERY = """
-- Doğrulama: Kolon durumunu kontrol et
SELECT
    engine_version,
    COUNT(*) AS count
FROM bina_analizleri
GROUP BY engine_version
ORDER BY engine_version;
""".strip()


def print_step(step_num, sql, description):
    """Migration adımını formatlı yazdır."""
    print(f"\n{'='*60}")
    print(f"  ADIM {step_num}: {description}")
    print(f"{'='*60}")
    print(f"\n{sql}\n")
    print(f"{'='*60}")
    print()
    print("  >> Bu SQL'i kopyalayip Supabase Dashboard > SQL Editor'da calistirin.")
    print()


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Supabase engine_version migration — SQL Helper (print-only)",
        epilog="NOT: Bu script SQL'i yalnizca ekrana yazdirir. "
               "Otomatik DB baglantisi YOKTUR. "
               "SQL'i Supabase Dashboard > SQL Editor'da calistirin.",
    )
    parser.add_argument(
        "--step",
        choices=["1", "2", "3", "verify", "all"],
        required=True,
        help="Gösterilecek adım: 1=add column, 2=backfill, 3=set default, verify=kontrol, all=tümü",
    )
    args = parser.parse_args()

    steps = {
        "1": (STEP_1_ADD_COLUMN, "Kolonu ekle (nullable, default yok)"),
        "2": (STEP_2_BACKFILL, "Legacy satirlari backfill et (v1_ensemble)"),
        "3": (STEP_3_SET_DEFAULT, "Yeni satirlar icin default ayarla (v2_fuzzy27)"),
        "verify": (VERIFY_QUERY, "Kolon durumunu kontrol et"),
    }

    if args.step == "all":
        for s in ["1", "2", "3", "verify"]:
            sql, desc = steps[s]
            print_step(s, sql, desc)
        print("="*60)
        print("  TUM ADIMLAR YUKARIDA LISTELENMISTIR.")
        print("  Her adimi sirayla SQL Editor'da uygulayip verify ile dogrulayin.")
        print("="*60)
        return

    sql, desc = steps[args.step]
    print_step(args.step, sql, desc)


if __name__ == "__main__":
    main()
