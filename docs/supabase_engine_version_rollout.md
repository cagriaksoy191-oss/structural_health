# Supabase Migration Runbook: `engine_version` Kolonu

> **Durum:** ✅ Başarıyla uygulandı (2026-03-19)
> **Hedef tablo:** `bina_analizleri`
> **Hazırlayan:** Faz 3 doğrulaması sonrası otomatik üretilmiştir
> **Son güncelleme:** 2026-03-19
>
> **Not:** Migration başarıyla tamamlanmıştır. Bu doküman artık yeniden uygulama için değil,
> **referans / rollback / audit** amacıyla korunmaktadır.

---

## 1. Amaç ve Kapsam

Bu runbook, `bina_analizleri` tablosuna `engine_version` TEXT kolonu eklemek için
üretim-güvenli bir adım-adım rehber sunar.

**Neden gerekli:**
- Backend (`routes/risk.py` satır 335) her insert'te `engine_version: "v2_fuzzy27"` gönderiyor
- Supabase tablosunda bu kolon henüz yoksa, PostgREST bu alanı **kaydetmeyebilir veya insert hatasına neden olabilir** — davranış Supabase/PostgREST konfigürasyonuna bağlıdır. Migration uygulanana kadar `engine_version` persistence'ı **garanti değildir**
- Migration uygulandığında: yeni kayıtlar `v2_fuzzy27` etiketi taşıyacak, eski kayıtlar `v1_ensemble` olarak işaretlenecek
- Bu sayede hangi karar motoruyla üretildiği her kayıtta izlenebilir olacak

**Kapsam dışı:**
- Bu migration sadece veri şemasını rollout'a hazırlar
- CAP kalibrasyonu veya frontend görünürlüğü bundan bağımsızdır
- Kod değişikliği gerektirmez — backend zaten hazır

---

## 2. Ön Koşul Checklist

Migration'a başlamadan önce şunları doğrulayın:

- [ ] Supabase Dashboard'a erişiminiz var
- [ ] `bina_analizleri` tablosunda SQL Editor kullanma yetkiniz var
- [ ] Backend şu anda çalışıyor ve yeni kayıtlar oluşturabiliyor
- [ ] Son test sonuçları yeşil (85/85 PASSED)
- [ ] Bu runbook'u tamamen okudunuz

---

## 3. Durdurma Kriterleri

Aşağıdaki durumlardan **herhangi biri** oluşursa **durdurun** ve devam etmeyin:

| Durum | Aksiyon |
|-------|---------|
| SQL Editor erişim hatası | Dashboard yetkilerini kontrol edin |
| Adım 1 sonrası kolon görünmüyor | Tablo adını doğrulayın (`bina_analizleri`) |
| Adım 2 sonrası NULL satır kalmışsa | WHERE koşulunu kontrol edin, tekrar çalıştırın |
| Backend insert hatası veriyor | Kolon adı çakışması olabilir — kolon tipini doğrulayın |

---

## 4. Adım Adım Rollout

### Adım 1: Kolonu Ekle (nullable, default yok)

**Ne yapar:** Tabloyu kesmeden yeni TEXT kolonu ekler. Mevcut satırlar NULL olarak kalır.

**Idempotent:** ✅ `IF NOT EXISTS` — kolon zaten varsa hata vermez, tekrar çalıştırılabilir.

```sql
-- Adım 1: Kolonu nullable + default'suz ekle
-- Mevcut satırlar NULL olarak kalır, hizmet kesintisi yok
ALTER TABLE bina_analizleri
ADD COLUMN IF NOT EXISTS engine_version TEXT;
```

**Doğrulama — hemen ardından çalıştırın:**

```sql
-- Kolon var mı kontrol et
SELECT column_name, data_type, column_default
FROM information_schema.columns
WHERE table_name = 'bina_analizleri'
  AND column_name = 'engine_version';
```

**Beklenen çıktı:**

| column_name | data_type | column_default |
|-------------|-----------|----------------|
| engine_version | text | NULL |

⛔ Satır dönmüyorsa → **Durdurun.** Tablo adını doğrulayın.

---

### Adım 2: Legacy Satırları Backfill Et

**Ne yapar:** `engine_version` NULL olan tüm mevcut satırları `v1_ensemble` olarak işaretler.

**Idempotent:** ✅ `WHERE engine_version IS NULL` — zaten backfill edilmiş satırları etkilemez.

```sql
-- Adım 2: Legacy satırları backfill et
-- NULL olan satırlar v1 ensemble ile üretilmişti
UPDATE bina_analizleri
SET engine_version = 'v1_ensemble'
WHERE engine_version IS NULL;
```

**Doğrulama — hemen ardından çalıştırın:**

```sql
-- NULL kalmış satır var mı?
SELECT
    engine_version,
    COUNT(*) AS count
FROM bina_analizleri
GROUP BY engine_version
ORDER BY engine_version;
```

**Beklenen çıktı:**

| engine_version | count |
|---------------|-------|
| v1_ensemble | (eski kayıt sayısı) |

⛔ NULL satır görünüyorsa → Adım 2'yi tekrar çalıştırın.

ℹ️ Eğer backend migration sırasında yeni kayıt eklediyse, `v2_fuzzy27` satırları da görünebilir — bu normaldir.

---

### Adım 3: Yeni Satırlar İçin Default Ayarla

**Ne yapar:** Bundan sonra insert edilen her satır otomatik olarak `v2_fuzzy27` alır.
Backend zaten bu değeri gönderiyor, ama default DB tarafında da güvence sağlar.

**Idempotent:** ✅ Tekrar çalıştırılabilir — var olan default'u günceller.

```sql
-- Adım 3: Yeni satırlar için default ayarla
ALTER TABLE bina_analizleri
ALTER COLUMN engine_version SET DEFAULT 'v2_fuzzy27';
```

**Doğrulama — hemen ardından çalıştırın:**

```sql
-- Default ayarlandı mı?
SELECT column_name, column_default
FROM information_schema.columns
WHERE table_name = 'bina_analizleri'
  AND column_name = 'engine_version';
```

**Beklenen çıktı:**

| column_name | column_default |
|-------------|----------------|
| engine_version | 'v2_fuzzy27'::text |

---

## 5. Final Doğrulama

Tüm adımlar tamamlandıktan sonra toplu doğrulama:

```sql
SELECT
    engine_version,
    COUNT(*) AS count
FROM bina_analizleri
GROUP BY engine_version
ORDER BY engine_version;
```

**Beklenen çıktı:**

| engine_version | count |
|---------------|-------|
| v1_ensemble | (eski kayıt sayınız) |
| v2_fuzzy27 | (varsa yeni kayıtlar) |

✅ NULL satır **olmamalı.**
✅ `v1_ensemble` ve/veya `v2_fuzzy27` satırları görünmeli.

---

## 6. Post-Migration Smoke Check

Migration sonrası backend'in doğru çalıştığını doğrulamak için:

### 6.1 Backend Insert Testi

1. Backend'i çalıştırın (`uvicorn main:app`)
2. Swagger UI'dan (`/docs`) veya frontend'den bir analiz çalıştırın
3. Supabase Dashboard'da `bina_analizleri` tablosunu açın
4. En son eklenen kaydın `engine_version` kolonunda `v2_fuzzy27` yazdığını doğrulayın

### 6.2 API Response Kontrolü

Swagger UI'dan `/api/risk-hesapla` endpoint'ine istek gönderin ve response'ta şunları kontrol edin:

```json
{
  "engineVersion": "v2_fuzzy27",
  "fuzzyTrace": {
    "raw_score": ...,
    "capped_score": ...,
    "fired_rules": [...],
    "applied_caps": [...]
  }
}
```

### 6.3 CSV / Supabase Tutarlılık Kontrolü

CSV dosyasındaki son satırı kontrol edin:

```powershell
Get-Content veri_kayitlari.csv | Select-Object -Last 1
```

Son sutunda `v2_fuzzy27` yazmalı. Bu değer Supabase'deki son kayıtla aynı olmalı.

### 6.4 Hata Kontrolü

Backend konsolunda şunlar **olmamalı:**
- `[HATA] Supabase Yazma Hatasi`
- `engine_version` ile ilgili herhangi bir PostgREST hatası

---

## 7. Sorun Giderme

### "Kolon zaten varsa ne olur?"

Adım 1'deki `IF NOT EXISTS` sayesinde hata oluşmaz. Kolon mevcutsa SQL sessizce geçer.

### "Backfill sırasında yeni kayıt gelirse?"

Backend `engine_version: 'v2_fuzzy27'` gönderiyor. Kolon Adım 1'de eklendikten sonra
yeni insert'ler bu değeri doğru şekilde yazar. Backfill sadece `NULL` satırları etkiler —
çakışma riski yoktur.

### "Migration geri alınabilir mi?"

```sql
-- SADECE GEREKİRSE: Kolonu tamamen kaldır
-- DİKKAT: Bu işlem engine_version verisini kalıcı olarak siler!
ALTER TABLE bina_analizleri DROP COLUMN IF EXISTS engine_version;
```

⚠️ Bu geri alma işlemi veri kaybına neden olur. Sadece ciddi sorun durumunda kullanın.

---

## 8. Operasyonel Notlar

- DDL adımları (`ALTER TABLE`) backend çalışırken uygulanabilir — tablo kilidini gerektirmez
- Ancak **migration öncesinde** backend'in `engine_version` alanını başarıyla kaydedebildiği garanti değildir. Migration'ı mümkün olan en kısa sürede uygulamak veri tutarlılığı açısından önemlidir
- Kolon nullable olduğu için Adım 1 sonrası insert akışı hata vermez — kolon eklendikten sonra backend değeri doğru şekilde yazar
- Default ayarlandıktan sonra bile backend kendi değerini explicit olarak gönderir — çift güvence
- Migration script referansı: `scripts/migrate_engine_version.py` (print-only SQL helper)
