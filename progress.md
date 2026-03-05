# Progress — Açık Görevler ve Notlar

> **Son güncelleme:** 2026-03-05

## Tartışıldı Ama Koda Dökülmedi (Backlog)

### P2 — Cache Eviction Eksikliği

- `services/afad_api.py` içindeki in-memory cache'te proaktif temizleme (eviction) yok
- Süresi dolan girdiler sadece tekrar sorgulandığında siliniyor
- 81 il × sınırlı sorgu = pratikte düşük risk ama uzun çalışan sunucuda birikebilir
- **Öneri:** `maxsize` limiti veya periyodik temizleme eklenebilir

### P2 — Max PGA Stratejisi Dokümantasyonu

- `calculate_pga_from_events()` tüm depremlerin max PGA'sını alıyor (conservative)
- Ön tarama için güvenli taraf (overestimate > underestimate) ama kullanıcıya abartılmış PGA sunulabilir
- **Öneri:** Detaylara bir uyarı notu eklenebilir ("Bu en kötü senaryo tahminidir" gibi)

### ~~Frontend Tam E2E Test~~ ✅ TAMAMLANDI

- `frontend/package.json` BOM fix yapıldı, byte-level doğrulandı
- `baslat.bat` ile frontend + backend birlikte çalıştırıldı, uçtan uca test edildi (2026-03-01 03:43)
- Afyonkarahisar/Çobanlar testi: healthScore=52, depremSeviye=ORTA, Beton=39.4 MPa, AI yorum üretildi ✅

## Çözülemeyen / Bilinen Kısıtlamalar

- AFAD TDTH (tdth.afad.gov.tr) e-Devlet yetkilendirmesi gerektiriyor — resmi PGA verisi alınamıyor
- AFAD Event API bazen HTTP 302 (e-Devlet redirect) atıyor — statik harita fallback her zaman devreye giriyor
- GMPE formülü basitleştirilmiş Boore-Atkinson esinli; resmi GMPE için TDTH verisi şart

## Yarının Görevleri

- [ ] P2 cache eviction değerlendirmesi (gerekli mi?)
- [x] Git push (bugünkü P0/P1 fix + BOM fix + Git Senkronizasyon Altyapısı eklendi)
- [ ] Frontend UI iyileştirmeleri (kullanıcının belirttiği geliştirme alanları)
