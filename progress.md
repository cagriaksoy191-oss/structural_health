# Project Progress

## Session Intent

Yapı Sağlığı İzleme (Structural Health Monitoring) — Web Tabanlı Ön Tarama Aracı. Kullanıcı bina verilerini girer, sistem deprem riski, yapısal skor, beton dayanımı, korozyon analizi, fuzzy logic ve ML ensemble ile sağlık skoru hesaplar, Qwen3 LLM ile Türkçe uzman yorumu üretir.

## Proje Mimarisi

### Backend: FastAPI (Python)

- **Giriş noktası:** `main.py` — FastAPI app, CORS ayarları, backward-compat re-export'lar
- **Konfigürasyon:** `config.py` — Supabase bağlantısı (SUPABASE_URL + SUPABASE_KEY), CSV_LOCK (thread safety)
- **Ortam değişkenleri:** `.env` dosyası (`.env.example` şablondan kopyalanır)
- **Port:** `127.0.0.1:8000` (uvicorn)
- **CORS:** `ALLOWED_ORIGINS` env var'ı ile virgülle ayrılmış origin listesi

### API Endpoint

- **POST** `/api/risk-hesapla` — Tek endpoint, `RiskRequest` alır, `RiskResponse` döner

### Modüler Klasör Yapısı

```text
main.py                    → FastAPI app + backward-compat re-exports
config.py                  → Supabase client + CSV_LOCK
models/schemas.py          → RiskRequest (17 alan) + RiskResponse (17 alan)
routes/risk.py             → /api/risk-hesapla endpoint (6 aşamalı pipeline)
services/
  normalize.py             → Türkçe karakter normalizasyonu (ğ→g, ş→s, ı→i)
  earthquake.py            → 81 il deprem risk haritası + zemin sınıfı (Z1-Z4) + AFAD hybrid
  afad_api.py              → AFAD Event API client + PGA hesaplama + in-memory cache
  structural.py            → 14 kritere göre yapısal skor hesaplama
  fuzzy_engine.py          → scikit-fuzzy 3-girdi/5-kural sistemi
  ml_models.py             → RandomForest beton + risk modeli (joblib)
  corrosion.py             → ASTM C876 korozyon olasılığı (sürekli interpolasyon)
  ai_comment.py            → Qwen3:8b LLM entegrasyonu (Ollama localhost:11434)
  data_service.py          → Supabase + CSV veri kayıt
```

### Risk Hesaplama Pipeline (6 Aşama)

1. **Deprem Analizi:** `earthquake.py` — il/ilçe bazlı risk seviyesi (yüksek/orta/düşük) + zemin sınıfı (Z1-Z4) tahmini
2. **Yapısal Skor:** `structural.py` — Yapım yılı, kat sayısı, hasar durumu, kısa kolon, çıkma, plan tipi, zemin sınıfı, çatlak puanı dahil 14 kriter, TBDY 2018 uyumlu
3. **Beton Dayanımı:** `ml_models.py` — UPV + Rebound Number → RandomForest ile MPa tahmini, TBDY 2018 minimum C25 kontrolü
4. **Korozyon:** `corrosion.py` — ASTM C876 standardı, -600 ile +100 mV arası sürekli interpolasyon, 5 seviye (Düşük → Çok Yüksek)
5. **Fuzzy + Ensemble:** `fuzzy_engine.py` + `ml_models.py` — Fuzzy Logic (strength, corrosion, survey_risk → health 0-100) %60 + RandomForest Classifier %40 ağırlıklı ensemble
6. **AI Yorum:** `ai_comment.py` — Qwen3:8b modeli (Ollama üzerinden), skor/risk/beton/korozyon verilerinden Türkçe uzman paragrafı üretir

### Fuzzy Logic Detayları

- **Girdiler:** strength (0-80 MPa), corrosion (-600 ile 100 mV), survey_risk (0-50 puan)
- **Çıktı:** health (0-100 skor)
- **Üyelik fonksiyonları:** trapmf + trimf
- **5 kural:** very_bad, bad, medium, good, very_good
- **Clamp mekanizması:** Girdiler fuzzy evren sınırlarına sınırlandırılır, uyarı loglanır

### ANFIS Modeli

- **Dosya:** `anfis.py` — PyTorch nn.Module, Gaussian üyelik fonksiyonları
- **Parametreler:** n_inputs, n_rules, center (c), sigma, consequent_weights, consequent_bias
- **Ağırlıklar:** `anfis_model_agirliklari.pth` (2.6 KB)
- **Eğitim:** `integrate_anfis_and_train.py` — Sentetik veri ile eğitim, scaler'lar: `scaler_x.pkl`, `scaler_y.pkl`

### ML Model Dosyaları

- `concrete_model.joblib` (4.2 MB) — Beton dayanımı tahmini (RandomForest Regressor)
- `risk_model.joblib` (8.5 MB) — Risk sınıflandırma (RandomForest Classifier, predict_proba)
- `etiket_encoder.joblib` — Label encoder
- `anfis_model_agirliklari.pth` — ANFIS PyTorch ağırlıkları
- `scaler_x.pkl`, `scaler_y.pkl` — ANFIS normalizasyon

### Pydantic Veri Modelleri

**RiskRequest (17 alan):**

- il, ilce, yapimYili (1800-güncel), katSayisi (1-100)
- zeminDukkan, bitisik, hasar, kullanimAmaci
- kisaKolon, agirCikma, planTipi, bitisikHiza
- ultrasonikSesHizi (gt=0), geriSicramaSayisi (gt=0)
- corrosion (mV), zeminSinifi (optional), crackPuan (0-3, optional)

**RiskResponse (17 alan):**

- healthScore, genelSeviye, aciklama
- depremSeviye, depremPuan, yapisalSeviye, yapisalPuan, toplamYapisalRisk
- zeminSinifi, basincDayanimi, detaylar (list)
- fuzzyLabel, corrosion, aiEtiket, aiYorum

### Frontend: React (Vite)

- **Ana:** `App.jsx` — State management (result, loading, error), API çağrısı, sonuç gösterimi
- **Bileşenler:**
  - `RiskForm.jsx` (11.7 KB) — 17 alanlı form, il/ilçe seçici
  - `ResultCard.jsx` (4.6 KB) — Sonuç kartı, skor, pill'ler, AI yorum kutusu
  - `Header.jsx` — Başlık bileşeni
- **Hooks:** `useGeolocation.js` — Tarayıcı konum API'si
- **Constants:** `cityData.js` (20.8 KB) — Tüm Türkiye il/ilçe listesi
- **API URL:** `http://127.0.0.1:8000/api/risk-hesapla`
- **Dev server:** Vite (localhost:5173)

### Veritabanı: Supabase

- **Tablo:** `bina_analizleri` — Her analiz sonucunun kaydı
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

- `scripts/gunsonu.ps1` (12.9 KB) — Gün sonu otomasyonu (git sync, test, deploy)
- `scripts/smart_sync.py` (11.6 KB) — Pinecone akıllı senkronizasyon
- `scripts/memory_prep_logic.py` (1.9 KB) — Memory-bank hazırlık
- `sentetik_veri_uret.py` — Sentetik bina verisi üreteci
- `train_model.py` — ML model eğitim scripti
- `integrate_anfis_and_train.py` — ANFIS entegrasyonu ve eğitimi
- `migrate_data.py` — Supabase veri migrasyon scripti
- `baslat.bat`, `kurulum.bat`, `git_bagla.bat` — Windows batch scriptleri

### Test Altyapısı

- `tests/` — Pytest test klasörü
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
- python-dotenv — .env yükleme
- supabase — Veritabanı
- pinecone-client, gitpython — Senkronizasyon
- matplotlib — Görselleştirme

### Workflow'lar (.agent/workflows)

- `/sabah` — Günü başlat: git pull, venv aktivasyonu
- `/gunsonu` — Gün sonu: CI/CD döngüsü, git sync, test
- `/test` — Lokal test: health check, sunucu
- `/gonder` — Git add, commit, push
- `/kontrol` — GitHub Actions durumunu kontrol et
- `/runner` — Self-hosted runner başlat
- `/compress` — Context sıkıştırma, progress.md güncelle

### Context Management Sistemi

- `CLAUDE.md` — Proje kuralları (her sohbette otomatik okunur)
- `progress.md` — Bu dosya (proje durumu, tek kaynak)
- MCP Memory-Bank — Dış hafıza (mcp_config.json'da yapılandırılmış)
- `/compress` workflow — Anchored Iterative Summarization stratejisi

### Dış Bağlantılar

- **Ollama:** localhost:11434 (Qwen3:8b modeli)
- **Supabase:** Cloud PostgreSQL
- **Pinecone:** Vektör veritabanı (proje hafızası)
- **GitHub:** cagriaksoy191-oss/structural_health

## Completed

- [x] Modular FastAPI refactoring (main.py → routes/, services/, models/)
- [x] CI/CD pipeline (GitHub Actions) — self-hosted runner active
- [x] Pinecone MCP integration + smart_sync.py
- [x] Supabase MCP integration + veri migrasyon
- [x] TestSprite test coverage setup (33 test dosyası)
- [x] Frontend (React/Vite) connected to backend API
- [x] ML model training (concrete_model, risk_model, ANFIS)
- [x] Fuzzy Logic sistemi (3 girdi, 5 kural, 5 çıktı seviyesi)
- [x] ASTM C876 korozyon modülü (sürekli interpolasyon)
- [x] Qwen3:8b LLM entegrasyonu (Ollama üzerinden)
- [x] Deprem haritası (81 il, ilçe bazlı risk + zemin sınıfı)
- [x] Yapısal skor hesaplama (14 kriter, TBDY 2018 uyumlu)
- [x] Ensemble model (Fuzzy %60 + RF %40)
- [x] Workflow scripts (/sabah, /gunsonu, /test, /gonder, /kontrol, /runner)
- [x] Context management entegrasyonu (CLAUDE.md, progress.md, memory-bank, /compress)
- [x] Backward compatibility (eski importlar main.py'den hala çalışır)
- [x] Sentetik veri üretme pipeline'ı
- [x] Supabase veri migrasyon scripti
- [x] AFAD Deprem Tehlike Haritası API entegrasyonu (hybrid: AFAD API + statik harita fallback)
- [x] PGA (Peak Ground Acceleration) hesaplama ve gösterimi
- [x] 81 il koordinat tablosu + AFAD Event API sorgusu
- [x] In-memory cache (TTL bazlı, 1 saat)
- [x] AFAD entegrasyon testleri (21 test)

## In Progress

- [ ] (Yeni görev eklendiğinde buraya yaz)

## Decisions

- Anchored Iterative Summarization stratejisi kullanılacak (context-compression)
- MCP Memory-Bank ile dış hafıza kullanılacak
- CLAUDE.md otomatik okunacak, PROJECT-RULES.md kaldırıldı
- Artifact-driven development: progress.md merkez belge
- Ensemble ağırlık: Fuzzy %60, RF %40 — daha yorumlanabilir sonuç
- TBDY 2018 minimum beton sınıfı (C25) kontrolü yapılıyor
- ASTM C876 sürekli interpolasyon (kesikli eşik yerine)
- Backward-compat: main.py'den eski importlar re-export ile korunuyor
- Supabase yoksa uygulama yedek modda (CSV-only) çalışır
- Fuzzy girdileri clamp ile sınırlandırılır, kullanıcıya uyarı verilir

## Files Modified (Son Oturum)

- services/afad_api.py: YENİ — AFAD Event API client + PGA hesaplama + cache
- services/earthquake.py: Hybrid sistem eklendi (deprem_analizi_async)
- models/schemas.py: RiskRequest'e lat/lon, RiskResponse'a pga/depremKaynak eklendi
- routes/risk.py: Pipeline async hale getirildi, AFAD entegrasyonu
- config.py: AFAD API ayarları eklendi
- .env.example: AFAD_CACHE_TTL eklendi
- requirements.txt: httpx eklendi
- frontend/src/hooks/useGeolocation.js: lat/lon return eklendi
- frontend/src/components/RiskForm.jsx: lat/lon form data'ya eklendi
- frontend/src/App.jsx: PGA ve kaynak pill'leri eklendi
- tests/test_afad_integration.py: YENİ — 21 test
- progress.md: Güncellendi

## Next Steps

- Frontend UI/UX iyileştirmeleri (modern tasarım, animasyonlar)
- Production deployment hazırlığı
- AFAD TDTH doğrudan PGA sorgusu (e-Devlet API key alınırsa)
- /compress workflow'unu uzun sohbette test et
