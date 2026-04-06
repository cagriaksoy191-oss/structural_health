# Progress — Açık Görevler ve Notlar

> **Son güncelleme:** 2026-04-06

## Backlog — Açık Görevler

### ~~v1 Fuzzy Kodu Temizliği~~ ✅ TAMAMLANDI (2026-03-29)

- `fuzzy_engine.py` içindeki v1 kodu (5 kural, `create_fuzzy_system`, `fuzzy_control_system`) kaldırıldı
- `main.py` re-export'larından `fuzzy_control_system` silindi
- `test_fuzzy_v2_faz1.py` v1 testleri kaldırıldı, `testsprite_tests/TC009` v2'ye migrase edildi

### ~~`risk_model.joblib` Kaldırma~~ ✅ TAMAMLANDI (2026-03-29)

- 8.5 MB dosya repodan kaldırıldı (`git rm`)
- `services/ml_models.py` içinden yükleme bloğu ve `rf_health_score()` silindi
- `main.py` re-export'larından `rf_health_score` silindi
- `tests/health_check.py` model listesinden çıkarıldı
- Training capability korundu: `train_model.py` hâlâ yeni model üretebilir

### Offline Eğitim Scripti Temizliği (Follow-up)

- `train_model.py` risk_model referansları
- `integrate_anfis_and_train.py` risk_model eğitim bölümü (concrete_model korunarak cerrahi düzenleme)
- `sentetik_veri_uret.py` kırık import'lar (`genel_risk_seviyesi`) + risk_model bağımlılığı
- `etiket_encoder.joblib` (sentetik_veri_uret.py ile birlikte)
- **Risk:** Düşük — tümü offline araçlar, runtime'a sıfır etkisi

### ~~CAP Kalibrasyon Refinement~~ ✅ TAMAMLANDI (2026-04-06)

- Masa başı teknik değerlendirme tamamlandı. `CAP_SINGLE=40` ve `CAP_DUAL=25` değerlerinin Faz 3 testleriyle çelişmediği ve etiket sınırlarında mantıklı olduğu doğrulandı. Saha verisi olmadan koda dokunulmadı.

### ~~AFAD Doğruluğu İyileştirmesi~~ ✅ TAMAMLANDI (2026-04-06)

- GMPE formülünde $h=10$ km nominal odak derinliği düzeltmesi uygulandı.
- Senaryo 3 (Honest Fallback) uygulandı. Yüksek riskli statik bölgede düşük AFAD aktivitesi olursa, sessizce tehlikeli olan statik veri kullanılıyor. Testleri doğrulandı.
- UI "Son 50 Yıl" metni 1 yıla düzeltildi.

## Yarının Görevleri / Sıradaki Adımlar

### Offline Scriptlerin Bakımı (Opsiyonel)
- Eğitim araçları (`train_model.py`, `sentetik_veri_uret.py`) `risk_model`'den tamamen temizlenebilir. Günlük işlemleri aksatmaz.

## Tartışıldı Ama Koda Dökülmedi

### Dinamik Baseline Kayıt İşlemi (Golden Tests İçin)
- Orijinalde "Golden Runtime Testleri" için baseline'ları (çıktıları) otomatik kaydedip (capture) ilerleyen testlerde dosyadakilere karşı denetleyen bir sistem planlandı.
- Ancak bu yaklaşımın, motor değiştirildiğinde sessizce kendi kendini doğrulayan bir regression anti-pattern'i üreteceğinden çekinildi.
- **Durum:** Koda dökülmedi. Sabit (hardcoded) expectation yöntemi kesin standart olarak benimsendi. Yeni cap/kurallarda geliştiricinin manuel kırması/düzeltmesi beklentisi kabul edildi.

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
