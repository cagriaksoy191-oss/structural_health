# Fuzzy Logic v2 — Karar Motoru Walkthrough

> **Motor versiyonu:** `v2_fuzzy27`
> **Durum:** Aktif (Faz 3 doğrulaması tamamlandı, 85/85 test yeşil)
> **Son güncelleme:** 2026-03-19

## Genel Bakış

Bu doküman, yapı sağlığı izleme sisteminin karar motorunun v1 ensemble'dan v2 fuzzy + policy layer mimarisine geçişini özetler. Geçiş 3 fazda tamamlanmıştır.

## Faz 1 — Staged Altyapı

**Hedef:** Mevcut v1 runtime'ı bozmadan v2 altyapısını hazırlamak.

**Yapılan işler:**
- `fuzzy_engine.py` içinde `RULE_MATRIX` (27 kural) tanımlandı
- `create_fuzzy_system_v2()` builder fonksiyonu oluşturuldu
- `compute_health_v2()` — 3 girdi (strength, corrosion, survey_risk) → health skoru
- `get_fired_rules()` — Explainability: hangi kurallar ne ağırlıkla ateşlendi
- `apply_policy_caps()` — TBDY/ASTM guardrail'leri
- v1 kodu korundu (backward-compat)

**Doğrulama:** 15/15 Faz 1 test + 21/21 AFAD regresyon testi yeşil.

## Faz 2 — Atomik Cutover

**Hedef:** v2 altyapısını aktif pipeline'a tek commit'le entegre etmek.

**Yapılan işler:**
- `routes/risk.py` — Ensemble kaldırıldı, `compute_health_v2()` aktif
- `models/schemas.py` — `engineVersion` ve `fuzzyTrace` alanları eklendi
- `services/data_service.py` — CSV ve Supabase'e `engine_version` yazılıyor
- `services/pdf_report.py` — PDF footer'a motor versiyonu eklendi
- `main.py` — Backward-compat re-export güncellemesi

**Kritik karar:** RF ensemble (%60 fuzzy + %40 RF) **kalıcı olarak kaldırıldı**. `risk_model.joblib` dosyası repoda kalıyor (silindi → `DEPRECATED` ibaresiyle) ama aktif runtime'da kullanılmıyor.

**Doğrulama:** 11/11 Faz 2 regression test yeşil.

## Faz 3 — Doğrulama ve Kalibrasyon

**Hedef:** v2 motorun sayısal tutarlılığını, deterministik davranışını ve güvenilirliğini kanıtlamak.

### Test Kapsamı (38 test)

| Kategori | Test Sayısı | Sonuç |
|----------|------------|-------|
| Boundary (27 kuralın temsili) | 14 + 8 corner | PASSED |
| Monotonicity (3 eksen) | 4 | PASSED |
| Determinism (5 × 10 tekrar) | 5 | PASSED |
| Explainability trace | 5 | PASSED |
| Policy guardrail | 12 | PASSED |
| Stability / Resolution | 3 | PASSED |
| Cap kalibrasyon | 6 | PASSED |

### Toplam Test Durumu

```
Faz 1 (test_fuzzy_v2_faz1.py)      :  15/15 PASSED
Faz 2 (test_faz2_regression.py)    :  11/11 PASSED
Faz 3 (test_faz3_validation.py)    :  38/38 PASSED
AFAD  (test_afad_integration.py)   :  21/21 PASSED
─────────────────────────────────────────────────────
TOPLAM                             :  85/85 PASSED
```

## Mimari — Fuzzy v2 Detayları

### 27 Kural Matrisi

3 girdi × 3 seviye = 27 kural (`RULE_MATRIX`):

| Girdi | Set Adı | MF Türü | Parametreler | Anlam |
|-------|---------|---------|-------------|-------|
| **strength** | `low` | trapmf | [0, 0, 15, 25] | Zayıf beton (< C25) |
| | `medium` | trimf | [20, 35, 50] | Standart beton |
| | `high` | trapmf | [40, 55, 80, 80] | Güçlü beton |
| **corrosion** | `high_risk` | trapmf | [-600, -600, -400, -300] | Ağır korozyon (negatif = tehlikeli) |
| | `medium_risk` | trimf | [-400, -275, -150] | Orta korozyon |
| | `low_risk` | trapmf | [-200, -100, 100, 100] | Düşük korozyon (güvenli) |
| **survey_risk** | `safe` | trapmf | [0, 0, 10, 15] | Yapısal sorun yok |
| | `medium` | trimf | [12, 25, 38] | Orta yapısal risk |
| | `high` | trapmf | [30, 40, 50, 50] | Yüksek yapısal risk |

> **Not:** Corrosion ekseni ters yönlüdür — düşük mV (orn. -500) = yüksek risk (`high_risk`),
> yüksek mV (orn. +50) = düşük risk (`low_risk`).

Her kural `id`, `inputs`, `output`, `rationale`, `references` alanlarına sahip — tam explainability.

### Policy Cap Guardrails

| Cap | Koşul | Skor Tavanı | Referans |
|-----|-------|-------------|----------|
| `CAP_SINGLE` (TBDY) | Beton < 25 MPa | 40 | TBDY 2018 minimum C25 |
| `CAP_SINGLE` (ASTM) | Korozyon ≤ -350 mV | 40 | ASTM C876 |
| `CAP_DUAL` | İkisi birden | 25 | Çift kritik kombinasyon |

**Not:** CAP değerleri provisional — saha verileriyle kalibre edilebilir.

### `fuzzyTrace` — API Response vs Internal Trace

`compute_health_v2()` zengin bir trace üretir. Ancak `routes/risk.py` bunu
`RiskResponse.fuzzyTrace` alanına yazarken **daraltır** — bazı alanlar yalnızca
route iç mantığında (detaylar, PDF) kullanılır, API response'a gönderilmez.

#### API Response Contract (`RiskResponse.fuzzyTrace`)

Aşağıdaki yapı, `routes/risk.py` satır 341-362'de oluşturulur ve
istemciye dönen gerçek JSON'dur:

```json
{
  "raw_score": 55.0,
  "capped_score": 40.0,
  "fired_rules": [
    {
      "id": "R14",
      "output": "medium",
      "activation": 0.67,
      "rationale": "Her üç faktör 'orta' → dengeli orta risk..."
    }
  ],
  "applied_caps": [
    {
      "cap_name": "TBDY_ONELEME_CAP",
      "effective": true,
      "original_score": 55.0,
      "capped_score": 40.0
    }
  ]
}
```

#### Internal Trace (route iç kullanımı)

`compute_health_v2()` → `get_fired_rules()` ve `apply_policy_caps()` ek alanlar
döndürür. Route bunları `detaylar` listesine ve PDF raporuna yazar, ama
`fuzzyTrace` response'una **dahil etmez**:

| Alan | Kaynak Fonksiyon | API'de | Route İç Kullanımı |
|------|-----------------|--------|-------------------|
| `fired_rules[].references` | `get_fired_rules()` | ❌ | — |
| `fired_rules[].membership_detail` | `get_fired_rules()` | ❌ | — |
| `applied_caps[].threshold` | `apply_policy_caps()` | ❌ | — |
| `applied_caps[].reason` | `apply_policy_caps()` | ❌ | `detaylar` listesine yazılır |
| `applied_caps[].recommendation` | `apply_policy_caps()` | ❌ | `detaylar` listesine yazılır |

**Gerçek `cap_name` değerleri:**
- `"TBDY_ONELEME_CAP"` — beton < 25 MPa
- `"ASTM_C876_CAP"` — korozyon ≤ -350 mV
- `"CAP_DUAL"` — ikisi birden

## Engine Version Akışı

```
Request → compute_health_v2()
       → fuzzyTrace (fired_rules + caps)
       → engineVersion = "v2_fuzzy27"
       → RiskResponse (API)
       → CSV kayıt (engine_version kolonu)
       → Supabase kayıt (engine_version kolonu)
       → PDF rapor (footer'da ENGINE_VERSION)
```

## Supabase Migration

3 adımlı güvenli rollout — `scripts/migrate_engine_version.py` (print-only SQL helper):

```
Adım 1: ALTER TABLE bina_analizleri ADD COLUMN IF NOT EXISTS engine_version TEXT;
Adım 2: UPDATE bina_analizleri SET engine_version = 'v1_ensemble' WHERE engine_version IS NULL;
Adım 3: ALTER TABLE bina_analizleri ALTER COLUMN engine_version SET DEFAULT 'v2_fuzzy27';
```

**Durum:** ✅ Canlı DB'ye başarıyla uygulandı (2026-03-19). Legacy kayıtlar `v1_ensemble`, yeni kayıtlar `v2_fuzzy27` olarak etiketlendi. Post-migration smoke check geçti.

**Detaylı runbook:** `docs/supabase_engine_version_rollout.md`

## Kalibrasyon Bulguları

| Bulgu | Detay | Risk |
|-------|-------|------|
| MF gap bölgeleri | Strength 15-20, 40-50 arası partition sum < 1.0 | Düşük — hesaplamayı engellemez |
| CAP_DUAL=25 | Tam label sınırında (Bad/Very Bad) | Düşük — tasarım gereği, saha verisiyle kalibre edilebilir |
| TBDY sınırı sıçraması | 24→26 MPa arası raw skor 6.4 birim | Düşük — MF transition gap, normal fuzzy davranış |

## Kalan Operasyonel Notlar

- [x] ~~Supabase `engine_version` migration (canlı DB)~~ — tamamlandı (2026-03-19)
- [x] ~~Frontend'de `engineVersion` / `fuzzyTrace` gösterimi~~ — tamamlandı (App.jsx, engine-meta + trace-panel)
- [ ] v1 fuzzy kodu temizliği (şu an backward-compat korunuyor)
- [ ] `risk_model.joblib` dosyasının repodan kaldırılması (boyut optimizasyonu)
- [ ] Saha verileriyle CAP_SINGLE / CAP_DUAL kalibrasyon refinement
