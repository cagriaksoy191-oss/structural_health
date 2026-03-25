# Progress — Açık Görevler ve Notlar

> **Son güncelleme:** 2026-03-26

## Backlog — Açık Görevler

### v1 Fuzzy Kodu Temizliği

- `fuzzy_engine.py` içinde v1 kodu (5 kural) backward-compat amaçlı korunuyor
- v2 artık %100 aktif → v1 güvenle silinebilir
- **Risk:** Düşük — v1'i import eden harici test/script kalmadığı doğrulanmalı

### `risk_model.joblib` Kaldırma

- 8.5 MB dosya repoda duruyor ama aktif runtime'da kullanılmıyor (DEPRECATED)
- Repo boyut optimizasyonu için kaldırılabilir
- **Risk:** Düşük — kullanılmıyor, silmek güvenli

### CAP Kalibrasyon Refinement

- CAP_SINGLE=40, CAP_DUAL=25 — provisional değerler
- Saha verileriyle kalibre edilmesi önerilir
- Faz 3 testleriyle mevcut değerler çelişmiyor

## Tartışıldı Ama Koda Dökülmedi

### Golden Runtime Testleri
- Aktif v2 pipeline için sabit referans girdi/çıktı vakaları üreten ayrı bir golden regression katmanı planlandı.
- Amaç: cleanup, cap review ve AFAD iyileştirmeleri öncesinde route-seviyesi operasyonel guardrail sağlamak.
- **Durum:** Tasarlandı, bugün kodlanmadı.

### AFAD Doğruluğu İyileştirmesi
- AFAD/GMPE tarafında yaklaşık PGA hesabının daha güvenilir hale getirilmesi konuşuldu.
- Bu iş, veri/saha gerçekliği olmadan en fazla heuristic/teknik review düzeyinde ilerleyebilir.
- **Durum:** Planlama seviyesinde, bugün kodlanmadı.

### Fallback Transparency Sonrası Kozmetik Follow-up
- Fallback transparency tamamlandı, ancak fallback anında frontend/PDF başlıklarının "Yapay Zeka ..." ifadesini koruması küçük bir kozmetik tutarsızlık yaratabilir.
- Mevcut durumda bu bir doğruluk veya API contract problemi değil; yalnızca düşük öncelikli UX/metin hizası işi.
- **Durum:** Bilinçli olarak bugün kapsam dışı bırakıldı.

### LLM Non-Determinism (Hallucination) Limitleri
- P1 düzeltmeleri kapsamında Qwen3:8b modelinin küçük ölçekli mimarisinden kaynaklı ikincil faktörleri (örneğin korozyonu) cümle bağlamak için rastgele kullanma eğilimi gözlemlendi.
- Prompt mühendisliği ile `ana_risk_kaynagi` değişkeni verilerek nedensellik hataları büyük ölçüde düzeltildi. Ancak küçük modellerin doğası gereği tam sentaktik determinizm her denemede garanti edilmeyebilir. Mevcut durumda maliyet/fayda optimizasyonu sebebiyle daha fazla karmaşık prompt zinciri kurulmadı.

### `/sabah` Scripti için `.venv` vs `venv` Sınırlaması
- Bugün README modernizasyonu sırasında `/sabah` (`scripts/sabah_rutini.ps1`) betiğinin öncelikli olarak sadece `venv` klasör yapısına göre tam tasarlandığı not edildi. Betik `.venv` desteklese de, fallback senaryoları tam hibrit değil.
- Bu durum bilinen bir kısıtlama olarak `README.md`'de belirtildi, ancak betiğin içinin tamamen agnostik yapılması koda dökülmedi.
- **Durum:** Bilinçli olarak kapsam dışı bırakıldı, projenin çalışmasına engel değil.

### P2 — Cache Eviction Eksikliği

- `services/afad_api.py` içindeki in-memory cache'te proaktif temizleme (eviction) yok
- Süresi dolan girdiler sadece tekrar sorgulandığında siliniyor
- 81 il × sınırlı sorgu = pratikte düşük risk ama uzun çalışan sunucuda birikebilir
- **Öneri:** `maxsize` limiti veya periyodik temizleme eklenebilir

### P2 — Max PGA Stratejisi Dokümantasyonu

- `calculate_pga_from_events()` tüm depremlerin max PGA'sını alıyor (conservative)
- Ön tarama için güvenli taraf (overestimate > underestimate) ama kullanıcıya abartılmış PGA sunulabilir
- **Öneri:** Detaylara bir uyarı notu eklenebilir

## Çözülemeyen / Bilinen Kısıtlamalar

- AFAD TDTH (tdth.afad.gov.tr) e-Devlet yetkilendirmesi gerektiriyor — resmi PGA verisi alınamıyor
- AFAD Event API bazen HTTP 302 (e-Devlet redirect) atıyor — statik harita fallback her zaman devreye giriyor
- GMPE formülü basitleştirilmiş Boore-Atkinson esinli; resmi GMPE için TDTH verisi şart
- `ResultCard.jsx` repoda mevcut ama aktif render path değil (Tailwind sınıfları, import edilmiyor)
- Gerçek cap kalibrasyonu için saha/etiketli veri gerekiyor; veri olmadan yapılacak cap çalışması ancak heuristic review seviyesinde kalır

## Bug Logs / Çözülenler

- Pinecone paket adı güncellendi ve ml_models.py emoji encoding hatası çözüldü
- **(2026-03-06)** Windows PowerShell (cp1254) UnicodeEncodeError — konsol emojiler ASCII taglarla değiştirildi
- **(2026-03-06)** VS Code "Select Python Interpreter" — `.vscode/settings.json` oluşturuldu
- **(2026-03-19)** fuzzyTrace walkthrough örneği API contract ile uyumsuzdu — route'un expose etmediği alanlar (references, membership_detail, threshold, reason, recommendation) kaldırıldı, API vs internal trace ayrımı netleştirildi
- **(2026-03-19)** Supabase rollout runbook "sessizce yok sayar" ifadesi fazla kesindi — teknik olarak savunulabilir dile düzeltildi
