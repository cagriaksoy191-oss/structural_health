# AGENTS.md — Proje Bağlam Dosyası

> **Amaç:** Her yeni sohbet başladığında AI modelinin bu dosyayı okuyarak projeye tam hakim olması.
> **Güncelleme:** Günün sonunda "AGENTS.md dosyasını bugün yaptığım değişikliklere göre güncelle" komutuyla güncellenir.

## Proje Tanımı

Yapı Sağlığı İzleme (Structural Health Monitoring) — Web Tabanlı Ön Tarama Aracı. Kullanıcı bina verilerini girer, sistem deprem riski, yapısal skor, beton dayanımı, korozyon analizi, v2 fuzzy logic (27 kural + policy layer) ile sağlık skoru hesaplar, Qwen3 LLM ile Türkçe uzman yorumu üretir.

## Proje Mimarisi

### Backend: FastAPI (Python)

- **Giriş noktası:** `main.py` — FastAPI app, CORS ayarları, backward-compat re-export'lar
- **Konfigürasyon:** `config.py` — Supabase bağlantısı, CSV_LOCK (thread safety), AFAD API ayarları
- **Ortam değişkenleri:** `.env` dosyası kullanılır (repoda şu anda `.env.example` şablonu bulunmuyor)
- **Port:** `127.0.0.1:8000` (uvicorn)
- **CORS:** `ALLOWED_ORIGINS` env var'ı ile virgülle ayrılmış origin listesi

### API Endpoint

- **POST** `/api/risk-hesapla` — Tek endpoint, `RiskRequest` alır, `RiskResponse` döner

### Modüler Klasör Yapısı

```text
main.py                    → FastAPI app + backward-compat re-exports
config.py                  → Supabase client + CSV_LOCK + AFAD API config
models/schemas.py          → RiskRequest (19 alan) + RiskResponse (24 alan, +engineVersion, +fuzzyTrace)
routes/risk.py             → /api/risk-hesapla endpoint (v2 fuzzy pipeline)
services/
  normalize.py             → Türkçe karakter normalizasyonu (ğ→g, ş→s, ı→i)
  earthquake.py            → 81 il deprem risk haritası + zemin sınıfı (Z1-Z4) + AFAD hybrid
  afad_api.py              → AFAD Event API client + PGA hesaplama + in-memory cache
  structural.py            → 14 kritere göre yapısal skor hesaplama
  fuzzy_engine.py          → v2 fuzzy motoru (27 kural, RULE_MATRIX, policy layer)
  ml_models.py             → RandomForest beton modeli (aktif) — risk_model cleanup ile kaldırıldı
  corrosion.py             → ASTM C876 korozyon olasılığı (sürekli interpolasyon)
  ai_comment.py            → Qwen3:8b LLM entegrasyonu (Ollama localhost:11434)
  data_service.py          → Supabase + CSV veri kayıt (kayit_ekle_supabase + kayit_ekle_csv)
  pdf_report.py            → FPDF2 ile yapı sağlığı PDF raporu (engine_version footer)
```

### Risk Hesaplama Pipeline (v2 — 6 Aşama)

1. **Deprem Analizi:** `earthquake.py` → `deprem_analizi_async()` — Hybrid: önce AFAD Event API (PGA hesaplama), başarısız olursa statik haritaya fallback. Koordinat bazlı veya il/ilçe bazlı sorgu destekler.
2. **Yapısal Skor:** `structural.py` — Yapım yılı, kat sayısı, hasar durumu, kısa kolon, çıkma, plan tipi, zemin sınıfı, çatlak puanı dahil 14 kriter, TBDY 2018 uyumlu
3. **Beton Dayanımı:** `ml_models.py` — UPV + Rebound Number → RandomForest ile MPa tahmini, TBDY 2018 minimum C25 kontrolü
4. **Korozyon:** `corrosion.py` — ASTM C876 standardı, -600 ile +100 mV arası sürekli interpolasyon, 5 seviye (Düşük → Çok Yüksek)
5. **Fuzzy v2 + Policy Layer:** `fuzzy_engine.py` → `compute_health_v2()` — 27 kural RULE_MATRIX, trapmf çıktılar, policy cap guardrails, explainability trace. RF ensemble kaldırıldı.
6. **AI Yorum:** `ai_comment.py` — Qwen3:8b modeli (Ollama üzerinden), skor/risk/beton/korozyon verilerinden Türkçe uzman paragrafı üretir

### Fuzzy Logic v2 Detayları

- **Motor versiyonu:** `v2_fuzzy27` (ENGINE_VERSION sabiti)
- **Girdiler:** strength (0-80 MPa), corrosion (-600 ile 100 mV), survey_risk (0-50 puan)
- **Çıktı:** health (0-100 skor)
- **Üyelik fonksiyonları:** trapmf + trimf (girdi), trapmf (çıktı)
- **27 kural:** RULE_MATRIX (3×3×3 tam kapsama), her kural id/inputs/output/rationale/references
- **Policy Layer:** TBDY C25 cap (CAP_SINGLE=40), ASTM C876 cap (CAP_SINGLE=40), çift kritik cap (CAP_DUAL=25)
- **Explainability:** `get_fired_rules()` + `apply_policy_caps()` → `fuzzyTrace` response alanı
- **Clamp mekanizması:** Girdiler fuzzy evren sınırlarına sınırlandırılır, uyarı loglanır

### ANFIS Modeli

- **Dosya:** `anfis.py` — PyTorch nn.Module, Gaussian üyelik fonksiyonları
- **Parametreler:** n_inputs, n_rules, center (c), sigma, consequent_weights, consequent_bias
- **Ağırlıklar:** `anfis_model_agirliklari.pth` (2.6 KB)
- **Eğitim:** `integrate_anfis_and_train.py` — Sentetik veri ile eğitim, scaler'lar: `scaler_x.pkl`, `scaler_y.pkl`

### ML Model Dosyaları

- `concrete_model.joblib` (4.2 MB) — Beton dayanımı tahmini (RandomForest Regressor)
- ~~`risk_model.joblib`~~ — **KALDIRILDI** (v1 cleanup ile repodan silindi, training scripti hâlâ üretebilir)
- `etiket_encoder.joblib` — Label encoder (offline script bağımlılığı)
- `anfis_model_agirliklari.pth` — ANFIS PyTorch ağırlıkları
- `scaler_x.pkl`, `scaler_y.pkl` — ANFIS normalizasyon

### Pydantic Veri Modelleri

**RiskRequest (19 alan):**

- il, ilce, yapimYili (1800-güncel), katSayisi (1-100)
- zeminDukkan, bitisik, hasar, kullanimAmaci
- kisaKolon, agirCikma, planTipi, bitisikHiza
- ultrasonikSesHizi (gt=0), geriSicramaSayisi (gt=0)
- corrosion (mV), zeminSinifi (optional), crackPuan (0-3, optional)
- **latitude (optional, float)** — Geolocation'dan gelen enlem
- **longitude (optional, float)** — Geolocation'dan gelen boylam

**RiskResponse (24 alan):**

- healthScore, genelSeviye, aciklama
- depremSeviye, depremPuan, yapisalSeviye, yapisalPuan, toplamYapisalRisk
- zeminSinifi, basincDayanimi, detaylar (list)
- fuzzyLabel, corrosion, aiEtiket, aiYorum
- **pga (optional, float)** — Peak Ground Acceleration (g cinsinden)
- **depremKaynak (optional, str)** — Veri kaynağı: "AFAD" veya "Statik Harita"
- bks (optional), binaYukseklik (optional), dts (optional), earthquakeClasses (optional)
- **pdfDownloadUrl (optional, str)** — PDF rapor indirme URL'i
- **engineVersion (optional, str)** — Karar motoru versiyonu (v2_fuzzy27)
- **fuzzyTrace (optional, Dict)** — Teknik explainability trace (fired_rules, applied_caps)

### Frontend: React (Vite)

- **Ana:** `App.jsx` — State management, API çağrısı, sonuç gösterimi (aktif rendering path)
  - Engine metadata satırı (`engineVersion` pill + raw/capped skor delta)
  - Teknik trace paneli (`<details>` accordion — fired rules + policy caps)
- **Bileşenler:**
  - `RiskForm.jsx` (11.7 KB) — 17 alanlı form, il/ilçe seçici
  - `ResultCard.jsx` (4.6 KB) — Repoda mevcut ama **aktif render path değil** (Tailwind sınıfları, import edilmiyor)
  - `Header.jsx` — Başlık bileşeni
- **Hooks:** `useGeolocation.js` — Tarayıcı konum API'si (lat/lon + il/ilçe döndürür)
- **Constants:** `cityData.js` (20.8 KB) — Tüm Türkiye il/ilçe listesi
- **Stil:** `legacy.css` — Vanilla CSS (pill, ai-box, engine-meta, trace-panel, rule-card, cap-card)
- **API URL:** `http://127.0.0.1:8000/api/risk-hesapla`
- **Dev server:** Vite (localhost:5173)

### Veritabanı: Supabase

- **Tablo:** `bina_analizleri` — Her analiz sonucunun kaydı
- **Kolon:** `engine_version` TEXT — Karar motoru versiyonu (canlı migration uygulandı, default: `v2_fuzzy27`)
- **Yedek mod:** Supabase yoksa konsola uyarı yazdırılır, uygulama çalışmaya devam eder
- **CSV yedek:** `veri_kayitlari.csv` (thread-safe, CSV_LOCK ile)

### Veri Dosyaları (CSV)

- `ana_veri.csv` (286 KB) — Ana eğitim verisi
- `beton_dataset_final.csv` (10 KB) — Beton dayanımı eğitim verisi (UPV, RN, MPa)
- `sentetik_bina_verisi.csv` (235 KB) — Sentetik bina verisi (risk modeli eğitimi)
- `veri_kayitlari.csv` (24 KB) — Uygulama kayıtları (gitignore'da)

### CI/CD: GitHub Actions

- **Workflow:** `.github/workflows/main.yml` — Self-hosted runner
- **Tetik:** Push to main
- **İşlemler:** Python setup, pip install, pytest, Pinecone sync

### Scriptler

- `scripts/sabah_rutini.ps1` — /sabah workflow statik scripti (hash-tabanlı cache, dizin doğrulama, git pull, bağımlılık kontrolü)
- `scripts/gunsonu.ps1` (12.9 KB) — Gün sonu otomasyonu (git sync, test, deploy)
- `scripts/smart_sync.py` (11.6 KB) — Pinecone akıllı senkronizasyon
- `scripts/migrate_engine_version.py` — Supabase engine_version kolonu migration (print-only SQL helper)
- `scripts/memory_prep_logic.py` (1.9 KB) — Memory-bank hazırlık
- `sentetik_veri_uret.py` — Sentetik bina verisi üreteci
- `train_model.py` — ML model eğitim scripti
- `integrate_anfis_and_train.py` — ANFIS entegrasyonu ve eğitimi
- `migrate_data.py` — Supabase veri migrasyon scripti
- `baslat.bat`, `kurulum.bat`, `git_bagla.bat` — Windows batch scriptleri

### Test Altyapısı

- `tests/` — Pytest test klasörü
  - `tests/test_fuzzy_v2_faz1.py` (14 test) — Faz 1 v2 fuzzy motor doğrulama
  - `tests/test_faz2_regression.py` (12 test) — Faz 2 route cutover regression
  - `tests/test_faz3_validation.py` (38 test) — Faz 3 boundary/mono/determ/explain/guard/stab/cap
  - `tests/test_golden_runtime.py` (6 test) — Faz 2/3'ten bağımsız, route bazlı E2E operasyonel sözleşme ve emergent behavior (cap presence, fallback, success) doğrulama
  - `tests/test_afad_integration.py` (21 test) — AFAD API entegrasyon testleri
  - `tests/test_fallback_transparency.py` (11 test) — Dürüst fallback ve hata sızdırmazlık testleri
  - `tests/quick_afad_test.py` — Hızlı API uçtan uca testi
  - `tests/health_check.py` — Sistem sağlık kontrolü
- `testsprite_tests/` (33 dosya) — TestSprite kapsamlı test suite
- `test_performans.py` — Performans testleri
- `test_supabase_integration.py` — Supabase entegrasyon testleri
- `test_request.py` — Manuel API test scripti

### Bağımlılıklar (requirements.txt)

- fastapi, uvicorn, pydantic — Web framework
- pandas, numpy (<2), scikit-learn (1.7.0), joblib — ML
- torch — PyTorch (ANFIS modeli)
- scikit-fuzzy, scipy, networkx — Fuzzy logic
- requests — HTTP (Ollama API)
- httpx — Async HTTP (AFAD API)
- fpdf2 — PDF rapor üretimi
- python-dotenv — .env yükleme
- supabase — Veritabanı
- pinecone, gitpython — Senkronizasyon
- matplotlib — Görselleştirme
- packaging — Versiyon karşılaştırma

### Workflow'lar (.agent/workflows)

- `/sabah` — Günü başlat: `scripts/sabah_rutini.ps1` tetikler (hash-tabanlı cache, tek dosya çalıştırma)
- `/gunsonu` — Gün sonu: CI/CD döngüsü, git sync, test
- `/test` — Lokal test: health check, sunucu
- `/gonder` — Git add, commit, push
- `/kontrol` — GitHub Actions durumunu kontrol et
- `/runner` — Self-hosted runner başlat
- `/compress` — Context sıkıştırma, progress.md güncelle

### Dış Bağlantılar

- **Ollama:** localhost:11434 (Qwen3:8b modeli)
- **AFAD Event API:** deprem.afad.gov.tr/apiv2/event/filter (JSON, halka açık)
- **AFAD TDTH:** tdth.afad.gov.tr (PGA haritası — e-Devlet gerekli, henüz entegre değil)
- **Supabase:** Cloud PostgreSQL
- **Pinecone:** Vektör veritabanı (proje hafızası)
- **GitHub:** cagriaksoy191-oss/structural_health

## Tamamlanan Geliştirmeler

- [x] Modular FastAPI refactoring (main.py → routes/, services/, models/)
- [x] CI/CD pipeline (GitHub Actions) — self-hosted runner active
- [x] Pinecone MCP integration + smart_sync.py
- [x] Supabase MCP integration + veri migrasyon
- [x] TestSprite test coverage setup (33 test dosyası)
- [x] Frontend (React/Vite) connected to backend API
- [x] ML model training (concrete_model, ANFIS) — risk_model KALDIRILDI
- [x] Fuzzy Logic v2 sistemi (27 kural, RULE_MATRIX + policy layer) — v1 (5 kural) KALDIRILDI
- [x] ASTM C876 korozyon modülü (sürekli interpolasyon)
- [x] Qwen3:8b LLM entegrasyonu (Ollama üzerinden)
- [x] Deprem haritası (81 il, ilçe bazlı risk + zemin sınıfı)
- [x] Yapısal skor hesaplama (14 kriter, TBDY 2018 uyumlu)
- [x] Ensemble model (Fuzzy %60 + RF %40) — **v2 ile kaldırıldı, yerine v2 fuzzy + policy layer**
- [x] Workflow scripts (/sabah, /gunsonu, /test, /gonder, /kontrol, /runner)
- [x] Context management entegrasyonu (CLAUDE.md, AGENTS.md, memory-bank, /compress)
- [x] Backward compatibility (eski importlar main.py'den hala çalışır)
- [x] Sentetik veri üretme pipeline'ı
- [x] Supabase veri migrasyon scripti
- [x] AFAD Deprem Tehlike Haritası API entegrasyonu (hybrid: AFAD API + statik harita fallback)
- [x] PGA (Peak Ground Acceleration) hesaplama ve gösterimi
- [x] 81 il koordinat tablosu + AFAD Event API sorgusu
- [x] In-memory cache (TTL bazlı, 1 saat)
- [x] AFAD entegrasyon testleri (21 test)
- [x] /sabah workflow optimizasyonu — SHA256 hash-tabanlı cache (.sabah_cache), pip/npm install sadece değişiklik varsa çalışır (~40dk → ~5sn)
- [x] Windows konsol emoji fix (UnicodeEncodeError) — konsol çıktıları ASCII, web UI emojileri korundu
- [x] VS Code Python interpreter config — `.vscode/settings.json` (`${workspaceFolder}\.venv`, `.gitignore`’da)

- [x] v2 Fuzzy Logic (27 kural RULE_MATRIX + policy layer + explainability) - Faz 1 staged altyapi
- [x] v2 Pipeline Cutover - Faz 2 atomik cutover (ensemble kaldirildi, compute_health_v2 aktif)
- [x] engineVersion / fuzzyTrace / CSV / PDF audit trail entegrasyonu
- [x] Faz 3 dogrulama ve kalibrasyon (85/85 test: boundary, monotonicity, determinism, explainability, guardrail)
- [x] Supabase migration hazirligi (scripts/migrate_engine_version.py - print-only SQL helper)
- [x] Supabase canli migration (engine_version kolonu — legacy: v1_ensemble, yeni: v2_fuzzy27)
- [x] Frontend engineVersion + fuzzyTrace gorunurlugu (App.jsx: engine-meta + trace-panel accordion)
- [x] Heuristic Cap Review — `CAP_SINGLE=40` ve `CAP_DUAL=25` eşiklerinin güvenliği doğrulandı
- [x] AFAD Doğruluğu İyileştirmesi (Scenario 3 - Honest Fallback) — 10km nominal odak, yüksek güvenlikli statik devir

## Mimari Kararlar

- Anchored Iterative Summarization stratejisi kullanılacak (context-compression)
- MCP Memory-Bank ile dış hafıza kullanılacak
- CLAUDE.md otomatik okunacak, PROJECT-RULES.md kaldırıldı
- **Karar motoru: %100 v2 Fuzzy + Policy Layer** (eski RF ensemble kaldırıldı)
- `concrete_model` (RF Regressor) aktif, `risk_model` (RF Classifier) **KALDIRILDI** (v1 cleanup — repodan silindi, ml_models.py'den temizlendi)
- **Fallback Transparency (availability-first):** Fuzzy motor exception durumunda response 200 korunur; `detaylar` ve `fuzzyTrace` üzerinden sanitize fallback sinyali döner, LLM yorumu ve `phase2_advice` deterministik fallback metnine geçer
- **Beton fallback sinyali:** `tahmin_beton_dayanimi()` içsel olarak `(value, used_fallback)` döner; 25.0 MPa varsayılanı sessiz kalmaz, route katmanında kullanıcıya uyarı verilir
- **PDF degrade modu:** PDF üretimi başarısız olursa ana risk response'u korunur; `pdfDownloadUrl=None` + detay uyarısı ile devam edilir, endpoint 500 vermez
- **Ollama sanitize:** LLM servis hataları kullanıcıya teknik exception leak etmeden Türkçe fallback metniyle döner; ham hata sadece log tarafında kalır
- CAP_SINGLE=40, CAP_DUAL=25 — provisional, Faz 3 testleriyle çelişmiyor
- MF gap bölgelerinde (strength 15-20, 40-50) partition sum < 1.0 — fuzzy tasarımın doğal sonucu
- TBDY 2018 minimum beton sınıfı (C25) policy cap olarak uygulanıyor
- ASTM C876 sürekli interpolasyon (kesikli eşik yerine) + policy cap (≤ -350 mV)
- Backward-compat: main.py'den aktif importlar re-export ile korunuyor (legacy `fuzzy_control_system` ve `rf_health_score` kaldırıldı)
- Supabase yoksa uygulama yedek modda (CSV-only) çalışır
- Fuzzy girdileri clamp ile sınırlandırılır, kullanıcıya uyarı verilir
- AFAD API → Hybrid yaklaşım: API-first, hardcoded-fallback (TDTH e-Devlet gerektirdiği için Event API kullanılıyor)
- AFAD PGA hesaplama: Basitleştirilmiş GMPE (Boore-Atkinson esinli), resmi PGA için TDTH lazım
- AFAD cache: In-memory dict + TTL (1 saat), Redis gerektirmez
- **AFAD cache kısıtlaması:** Tek-worker (uvicorn) senaryoda GIL + asyncio sayesinde thread-safe. Çoklu-worker'da (gunicorn -w N) her process kendi cache kopyasını tutar — paylaşımlı cache için Redis'e geçiş gerekir
- Pipeline artık async (`async def risk_hesapla`) — httpx async HTTP sorguları için
- **AI yorum (Ollama) async fix:** `get_llm_comment()` senkron `requests.post` (120s timeout) kullanıyor; `asyncio.to_thread()` ile thread pool'a atılıyor — event loop bloklanmaz, backward compat korunur
- **AFAD konfigürasyon merkezileştirmesi (DRY):** Tüm AFAD sabitleri (`AFAD_API_BASE_URL`, `AFAD_TIMEOUT`, `AFAD_CACHE_TTL`) `config.py`'de tanımlı, `afad_api.py` bunları import eder
- Frontend geolocation lat/lon bilgisi backend'e gönderiliyor (koordinat bazlı AFAD sorgusu için)
- **Git Senkronizasyon (v2):** `/gunsonu` komutu `Fetch -> Stash -> Pull -> Pop -> Conflict Check -> Test -> Commit -> Push` mimarisiyle çalışır. Çakışma anında (Exit Code 99) otomatik `--rebase` YAPILMAZ, sessiz veri kaybı engellenir.
- **Semantik Birleştirme Anayasası:** `.agent/workflows/gunsonu.md` içinde tanımlanmıştır. AI modelleri çakışmaları çözerken iki tarafın da emeğini korur, hiçbir kodu/görevi silmez, anlamsal birleştirme yapar.
- **Cross-machine Venv:** `scripts/gunsonu.ps1` hem `.venv` hem de `venv` dizinlerini dinamik olarak algılar.

## Son Değişiklikler

### v1 Fuzzy + risk_model.joblib Cleanup (2026-03-29)

- **risk_model.joblib (8.5 MB) repodan kaldırıldı:** `services/ml_models.py` içinden `RISK_MODEL_PATH`, `risk_model` yükleme bloğu ve `rf_health_score()` fonksiyonu silindi. `concrete_model` ve `tahmin_beton_dayanimi()` korundu.
- **v1 fuzzy engine kaldırıldı:** `services/fuzzy_engine.py` içinden `create_fuzzy_system()` (5 kural) ve `fuzzy_control_system` modül-seviye init silindi. v2 altyapısı (`compute_health_v2`, `RULE_MATRIX`, policy layer) korundu.
- **main.py re-export temizliği:** `fuzzy_control_system` ve `rf_health_score` backward-compat re-export'ları kaldırıldı (grep ile 0 dış tüketici doğrulandı). Aktif semboller korundu.
- **Test güncellemeleri:** `test_fuzzy_v2_faz1.py` v1 testleri kaldırıldı; `testsprite_tests/TC009` v2'ye migrase edildi; `health_check.py` model listesi güncellendi.
- **Offline scriptler kapsam dışı:** `train_model.py`, `integrate_anfis_and_train.py`, `sentetik_veri_uret.py`, `etiket_encoder.joblib` — follow-up olarak kaydedildi.
- **Doğrulama:** Golden Runtime (6), Faz 2 (12), Faz 3 (38), Faz 1 (14), Fallback (11), AFAD (21) test suiteleri geçirildi.

### Operasyonel Referans Katmanı (Golden Runtime Tests) (2026-03-27)

- **Golden Runtime Suite:** Faz 2 (wiring) ve Faz 3 (matematiksel boundary) testlerinden izole, API'nin bütünleşik davranışını (emergent behavior) ve dış sözleşmesini (contract) donuklaştıran E2E koruma katmanı eklendi.
- **Canonical Senaryolar:** `ROUTES.RISK` düzeyinde dış servisler (AFAD, LLM, DB, PDF) izole edildi; Sağlıklı, TBDY Cap Presence, ASTM Cap Presence, Dual Cap Presence, AFAD Success ve Statik Fallback olmak üzere 6 değişmez baseline expectation uygulandı. Test dinamiği kendini doğrulayan capture stratejisi yerine "hardcoded contract" ile regresyon zırhına dönüştürüldü.
- **Semantik Doğruluk (Presence vs. Clamp):** Motor matematiğine göre raw_score'un cap eşiklerinin hep altında kaldığı düşük değer durumları tespit edildi. Bunlar hatalı `effective=True` (clamp) beklentisinden arındırılarak `*_cap_presence` isimleriyle yalnızca "trace varlığı" denetleyecek dürüst ve gerçekçi bir formata çekildi. 
- **Durum:** Testler terminalde hatasız onaylandı (Total Suite: 88 PASS). v1 fuzzy + risk_model cleanup operasyonu bu testlerin koruması altında tamamlandı.

### Batch Script Modernizasyonu (2026-03-21)

- **`baslat.bat` Güvenilirliği:** Backend `cmd /k` relative path ile başlatılarak iç içe tırnak karmaşası ve boşluklu dizin kırılganlığı (nested quote parsing issues) tamamen çözüldü. Gerçek terminalde başarıyla smoke-check testinden geçti (Backend API ve Frontend erişilebilir).
- **`kurulum.bat` İyileştirmeleri:** Hardcoded paket listesi silindi; `requirements.txt` ve `npm install` tabanlı otomasyona geçildi. Bozuk veya kısmi `venv` ortamları `Scripts\python.exe` kontrolüyle engellendi.
- **Terminal Ön Kontrolleri:** Dinamik `.venv` / `venv` tespiti, `python` / `py -3` fallback stratejisi, `npm` ve `node_modules` preflight kontrolleri scriptlere sorunsuz entegre edildi.

### P0/P1 Hata Düzeltmeleri ve Repo Hijyeni (2026-03-21)

- **[P0] PDF Thread-Safe Backend (Crash Fix):** `services/pdf_report.py` içinde Matplotlib'in 0x80000003 uygulama çökmelerine yol açmasını engellemek için `import pyplot` öncesinde `matplotlib.use('Agg')` eklendi. Arkaplan thread'inde PDF grafik üretimi cross-thread olarak izole edildi ve güvenli hale getirildi.
- **[P1] AI Hatalı Nedensellik (Causality) Çözümü:** İkincil parametrelerin (orta-düşük korozyon) LLM tarafından "Aciliyet" nedeni sanılması engellendi. `routes/risk.py` içerisinde `ana_risk_kaynagi` ("Düşük Beton", "Kritik Korozyon" vb.) değerlendirilerek API response dışı arkaplan bağlamıyla `services/ai_comment.py`'ye iletildi. Prompta katı kurallarla aciliyet izahı sadece belirlenen ana kaynağa yüklendi.
- **Mimarinin Korunması:** Tüm API endpoint'leri, `fuzzy_engine.py`, UI katmanı hiçbir hasar veya schema değişikliği almadan korundu.
- **Testler:** `tests/test_faz2_regression.py` içine yeni bağlamları denetleyen sertifikasyon assert'leri eklendi.

### Git Çakışma Önleme Sistemi (2026-03-05)

- **Açıklar Kapatıldı:** `gunsonu.ps1` yeniden yazılarak eski "Commit -> Pull -> Push" akışındaki çakışma ve sessiz ezme (rebase) riskleri %100 giderildi.
- **Akıllı 4'lü Yol:** FULL SYNC, PULL-ONLY, FAST PATH, NO-OP yolları eklendi.
- **Exit Code 99:** Stash pop veya pull sırasında conflict çıkarsa script anında durur, AI'dan manuel çözüm bekler.
- **Semantik Birleştirme:** Tüm AI'lar için `AGENTS.md` ve `progress.md` özelinde hiçbir maddenin silinmemesini şart koşan "anlamsal birleştirme anayasası" eklendi (`gunsonu.md`).
- **Gün İçi Farkındalık:** Takımın pushlarını kontrol eden salt-okunur `/sync` komutu eklendi (`.agent/workflows/sync.md`).
- **Dinamik Pathler:** `.venv` ve `venv` desteklenecek şekilde health check ve dependency sync dinamikleştirildi.

### Windows Konsol Emoji Fix + VS Code Interpreter (2026-03-06)

- **UnicodeEncodeError:** Windows PowerShell (cp1254 encoding) konsol `print()` satırlarındaki UTF-8 emojiler ASCII taglarla değiştirildi (`[BASARILI]`, `[HATA]`, `[UYARI]`). Etkilenen dosyalar: `config.py`, `services/ml_models.py`, `services/data_service.py`, `services/ai_comment.py`, `scripts/smart_sync.py`, `debug_import.py`, `migrate_data.py`, `test_supabase_integration.py`, `test_performans.py`, `testsprite_tests/run_all_testsprite_tests.py`.
- **UI Emojileri Korundu:** API response’lardaki web sitesi emojileri (`corrosion.py` 🟢🟡🟠🔴, `risk.py` 📡📋🚨🤖) değiştirilmedi.
- **VS Code Interpreter:** `.vscode/settings.json` oluşturuldu (`python.defaultInterpreterPath: ${workspaceFolder}\.venv\Scripts\python.exe`). `.vscode/` `.gitignore`’da olduğu için ekip üyelerini etkilemez.

### AFAD Entegrasyonu Mimari Denetim & Düzeltmeleri

- **P0 Fix (Async Blocker):** `routes/risk.py` — `get_llm_comment()` çağrısı `asyncio.to_thread()` ile sarıldı; event loop artık LLM inference sırasında bloklanmaz
- **P1 Fix (DRY):** `afad_api.py` — Hardcoded AFAD sabitleri silindi, `config.py`'den import ediliyor; `config.py`'ye `AFAD_TIMEOUT` eklendi
- **P1 Fix (Dokümantasyon):** AGENTS.md Mimari Kararlar'a cache kısıtlaması ve async düzeltme notları eklendi
- **Backward compat:** `ai_comment.py` dokunulmadı, eski `get_llm_comment` importları çalışmaya devam ediyor

### Frontend BOM Fix

- `frontend/package.json` — UTF-8 BOM (EF BB BF) kaldırıldı; Vite PostCSS config yükleyicisi `JSON.parse()` BOM'u parse edemiyordu
- 767 → 764 byte (sadece BOM silindi, içerik aynı)
- Hata: `[plugin:vite:css] Failed to load PostCSS config: Unexpected token ''`

### /sabah Workflow Optimizasyonu (2026-02-28)

- `.agent/workflows/sabah.md` — Adım 2 tamamen yeniden yazıldı: SHA256 hash-tabanlı akıllı bağımlılık kontrolü
- `.gitignore` — `.sabah_cache` eklendi
- **Mekanizma:** requirements.txt ve package.json SHA256 hash'leri `.sabah_cache` (JSON) dosyasında tutulur, değişiklik yoksa pip/npm install atlanır
- **Loglama:** `--quiet` ve `Out-Null` kaldırıldı, `--progress-bar off` (pip) ve `--loglevel warn` (npm) kullanılıyor
- **Test sonucu:** 4/4 PASS — cache yok, değişiklik yok (12ms), requirements değişikliği, package.json değişikliği

### /sabah Statik Script Taşıma

- `scripts/sabah_rutini.ps1` oluşturuldu — tüm inline PowerShell mantığı statik dosyaya taşındı
- `.agent/workflows/sabah.md` sadeleştirildi — tek satır tetikleyici: `powershell -ExecutionPolicy Bypass -File scripts\sabah_rutini.ps1`
- **Dizin güvenliği:** Script başlangıcında `main.py`, `requirements.txt`, `AGENTS.md` varlık kontrolü (yanlış dizin koruması)
- **Problem çözüldü:** Agent multiline PowerShell'i terminale yapıştırma → ParserError döngüsü ortadan kalktı

### Yeni Dosyalar

- `services/afad_api.py` — AFAD Event API client (280 satır): 81 il koordinat tablosu, async HTTP sorgu, GMPE PGA hesaplama, TTL cache
- `tests/test_afad_integration.py` — 21 birim testi: koordinat, cache, PGA, risk, hybrid, backward-compat
- `tests/quick_afad_test.py` — Hızlı API uçtan uca test scripti

### Değiştirilen Dosyalar (2026-02-28)

- `services/earthquake.py` — `deprem_analizi_async()` hybrid fonksiyonu eklendi (mevcut sync fonksiyonlar korundu)
- `models/schemas.py` — RiskRequest: +latitude, +longitude; RiskResponse: +pga, +depremKaynak
- `routes/risk.py` — Endpoint `async def` yapıldı, AFAD hybrid pipeline entegre edildi, detaylara kaynak bilgisi eklendi
- `config.py` — AFAD_API_BASE_URL ve AFAD_CACHE_TTL sabitleri eklendi
- `.env.example` (historical, şu an repoda yok) — AFAD_CACHE_TTL opsiyonel ayarı eklendi
- `requirements.txt` — httpx bağımlılığı eklendi
- `frontend/src/hooks/useGeolocation.js` — lat/lon return değerleri eklendi
- `frontend/src/components/RiskForm.jsx` — formData'ya latitude/longitude eklendi, backend'e gönderiliyor
- `frontend/src/App.jsx` — Sonuç kartına PGA pill'i ve kaynak (AFAD/Statik) pill'i eklendi

### Değiştirilen Dosyalar (2026-03-01)

- `routes/risk.py` — `asyncio` import + `get_llm_comment` çağrısı `asyncio.to_thread()` ile sarıldı (P0 fix)
- `config.py` — `AFAD_TIMEOUT` sabiti eklendi (P1 DRY fix)
- `services/afad_api.py` — Hardcoded sabitler silindi, `config.py`'den import; kullanılmayan `os` import kaldırıldı (P1 DRY fix)
- `frontend/package.json` — UTF-8 BOM kaldırıldı (Vite PostCSS fix)

### Test Sonuçları (2026-02-28)

- `tests/test_afad_integration.py`: 21/21 PASSED ✅
- `testsprite_tests/TC015_earthquake_risk_map_verification.py`: 4/4 PASSED ✅ (backward-compat)
- Swagger UI API testi: İstanbul/Kadıköy → healthScore=53, depremSeviye=yüksek, kaynak=Statik Harita ✅
- AFAD API: HTTP 302 (e-Devlet redirect) → Fallback düzgün çalıştı ✅
- Health Check: TÜM KRİTİK KONTROLLER BAŞARILI ✅
- Git Push: Başarılı (13 dosya, +719/-16 satır) ✅

### Test Sonuçları (2026-03-01)

- `tests/test_afad_integration.py`: 21/21 PASSED ✅ (P0/P1 fix sonrası regresyon yok)
- Backward compat import testleri: `ai_comment`, `afad_api`, `risk.py`, `config.py` tümü OK ✅
- `frontend/package.json` BOM fix: byte-level doğrulama (0x7B ile başlıyor) ✅

### Supabase Canli Migration + Frontend Explainability (2026-03-19)

- **Supabase engine_version canli migration:** 3 adimli rollout SQL Editor'da basariyla uygulandi. Legacy kayitlar v1_ensemble, yeni kayitlar v2_fuzzy27. Post-migration smoke check gecti.
- **Frontend engineVersion gorunurlugu:** App.jsx - engine-meta satiri (motor versiyonu pill + raw/capped skor delta, PDF'e bagli degil)
- **Frontend fuzzyTrace paneli:** App.jsx - details accordion (varsayilan kapali): fired rules kartlari + policy caps kartlari (effective durumuna gore kirmizi/gri ayrim)
- **CSS:** legacy.css - engine-meta, trace-panel, rule-card, cap-card, cap-effective/cap-ineffective siniflari eklendi
- **Null-safe rendering:** Tum opsiyonel alanlar optional chaining + fallback ile korunuyor
- **Walkthrough duzeltmesi:** docs/fuzzy_v2_walkthrough.md - fuzzyTrace API contract hizalamasi, migration durumu guncellendi
- **Rollout runbook:** docs/supabase_engine_version_rollout.md - durum uygulandi olarak guncellendi
- **Frontend build:** npm run build - vite v7.3.1, hatasiz (514ms, 227 KB gzip)

### /sabah Venv Tutarlılığı + Fallback Şeffaflığı (2026-03-26)

- **`scripts/sabah_rutini.ps1` hizalaması:** `/sabah` artık `.venv\Scripts\python.exe` → `venv\Scripts\python.exe` sırasıyla geçerli ortamı seçer; ortam yoksa yeni `venv` oluşturmaz, kullanıcıyı `kurulum.bat` dosyasına yönlendirir.
- **`/sabah` sağlık kontrolü:** Hash cache korunurken `fastapi`, `torch`, `skfuzzy`, `supabase`, `httpx`, `dotenv` proxy import kontrolü eklendi; hash eşleşse bile ortam bozuksa `pip install` zorlanır.
- **Dokümantasyon hizası:** `README.md` ve `.agent/workflows/sabah.md`, `/sabah`ın ilk kurulum değil mevcut `.venv` / `venv` ortamını doğrulayan workflow olduğunu yansıtacak şekilde güncellendi.
- **Fuzzy fallback görünürlüğü:** `routes/risk.py` tarafında fuzzy motor exception durumları artık sessiz değil; `detaylar` ve `fuzzyTrace` içinde sanitize fallback sinyalleri dönüyor.
- **LLM/PDF dürüst fallback:** Fuzzy fallback sırasında normal LLM yorumu atlanıyor, `aciklama` / `aiYorum` / `phase2_advice` aynı dürüst fallback semantiğine çekiliyor; PDF hataları ana endpoint'i düşürmüyor.
- **Beton / log hijyeni:** `tahmin_beton_dayanimi()` explicit fallback sinyali dönüyor, `services/ai_comment.py` teknik hata leak etmiyor, `services/data_service.py` `print()` yerine logger kullanıyor.
- **Kanıt:** `tests/test_fallback_transparency.py` (11), `tests/test_faz2_regression.py` (12), `tests/test_faz3_validation.py` (38), `tests/test_afad_integration.py` (21), `tests/test_fuzzy_v2_faz1.py` (15) → toplam **97/97 PASSED**.

### README.md Modernizasyonu ve Repozitory Hijyeni (2026-03-26)

- **Repo-Gerçekliği Hizalaması:** `README.md` projenin güncel mimarisiyle %100 uyumlu hale getirildi. Artık v2 Fuzzy Logic (27 Kural + Policy Layer) ana karar motoru olarak vitrine çıkarıldı, eski ensemble modeller (v1 ve risk_model) dokümantasyondan temizlendi.
- **Sınırlamaların Dürüst Beyanı:** Ollama (Qwen3) zorunluluk değil, "AI yorum özelliği için opsiyonel" olarak konumlandırıldı; AI yorumları, Supabase ve PDF üretimi de dahil olmak üzere dürüst fallback katmanlarına sahip olduğu açıkça belirtildi.
- **Güvenli Başlatma Akışı (Happy Path):** Hızlı Başlangıç bölümü Windows terminal (`kurulum.bat` ve `baslat.bat`) öncelikli olacak şekilde güncellendi.
- **Venv/Interpreter Netliği:** Manuel başlatma komutlarına `.venv\Scripts\python.exe` / `venv\Scripts\python.exe` ibaresi eklendi; kullanıcıyı global Python yürütme hatasından koruyacak uyarılar dahil edildi.
- **Doğrulama ve Test:** Dış bağımlılık gerektiren `pytest` komutu yerine, repodan out-of-the-box çıkan `python tests/health_check.py` smoke-check testi birincil doğrulama aracı olarak öne çıkarıldı.

### Heuristic Cap Review (2026-04-06)

- Değişiklik uygulanmadı, ancak "Masa başı" teknik değerlendirme tamamlandı. `CAP_SINGLE=40` ve `CAP_DUAL=25` değerleri, mevcut etiket skalası taban/tavan sınırlarında savunulabilir ve Faz 3 & Golden Runtime testleri ile %100 tutarlı bulundu. Ampirik saha verisi (ground truth) sağlanana kadar kod üzerinde oynama yapılmayacak.

### AFAD Doğruluğu İyileştirmesi (Scenario 3 - Honest Fallback) (2026-04-06)

- **Hypocentral Distance Düzeltmesi:** `services/afad_api.py` içerisinde PGA tahmini yapan GMPE fonksiyonuna 10 km nominal odak derinliği ($h=10$) eklendi. Bu sayede merkez üssü senaryosunda olası matematiksel sızıntılar (boundary explosions) durduruldu.
- **Honest Fallback (Senaryo 3):** `services/earthquake.py` içerisinde, eğer AFAD'ın tespit ettiği anlık sismik risk, statik tehlike haritasının altındaysa, kullanıcıya yanlış güven aşılamamak adına sonuç otomatik olarak statik rejimine çekiliyor (`pga=None` atanarak karışık sinyal engelleniyor).
- **İç/Dış Sözleşme Uyumu:** `depremKaynak` API sözleşmesi ("AFAD" / "Statik Harita") tamamen korundu. Toplanan AFAD event logları şeffaflık adına iç yapıda (UI `earthquakeClasses` seviyesi için) taşınıyor, fakat API Response'a `events` olarak sızdırılmıyor. UI üzerindeki "Son 50 Yıl" metni de gerçek API limiti olan "Son 1 Yıl" ile güncellendi.
- **Golden Test Güvencesi:** Tüm "Honest Fallback" senaryoları mock ve sözleşme bazlı (90/90 passed) testlerle kilitli ve kanıtlı biçimde uyarlandı. Hiçbir regresyon söz konusu değil.

