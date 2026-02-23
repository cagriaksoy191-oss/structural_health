# 🏗️ Yapı Sağlığı Projesi — Stratejik Vizyon ve Mimari Değerlendirme Raporu

> **Hazırlayan:** Kıdemli Teknik Mimar & Startup Baş Danışmanı  
> **Tarih:** 24 Şubat 2026  
> **Kapsam:** Tüm codebase derinlemesine analizi (30+ dosya, ~3.500 satır)  
> **Ekip Büyüklüğü:** 4 Kişi  
> **Revizyon:** v2 — Madde 1 (API Güvenliği) tamamlanarak çıkartıldı ✅

---

## Yönetici Özeti

Proje, Türkiye'ye özgü deprem mühendisliği problemini çözen, **teknik açıdan ciddi potansiyele sahip** bir ön tarama aracıdır. Fuzzy Logic + LLM (Qwen3) + RandomForest üçgeni doğru bir temel oluşturuyor. Ancak kodda **kullanılmayan modeller, mimari darboğazlar ve UX fırsatları** tespit edildi. Aşağıdaki rapor, projeyi **sektörde rakipsiz** seviyeye taşıyacak somut adımları içermektedir.

---

## 🔴 KRİTİK (Hemen Yapılmalı)

### 1. Eğitilmiş Model Hiç Kullanılmıyor!

> **ÖNEMLİ:** `risk_model.joblib` (8.4 MB RandomForest) eğitilmiş ve klasörde duruyor, ancak `main.py` içinde **hiçbir yerde yüklenmemiyor veya kullanılmıyor**. Aynı şekilde `anfis.py` deki ANFIS modeli de tamamen **ölü kod**.

| Model | Durum | Dosya |
|-------|-------|-------|
| `concrete_model.joblib` | ✅ Aktif — UPV+RN → MPa tahmini yapıyor | `main.py` satır 319-337 |
| `risk_model.joblib` | ❌ Eğitildi ama asla çağrılmıyor | `train_model.py` |
| `anfis_model_agirliklari.pth` | ❌ ANFIS tanımlı ama entegre değil | `anfis.py` |

**Çözüm:** `risk_model.joblib`'i `main.py`'ye yükleyerek Fuzzy Logic sonucuyla **ensemble** (ağırlıklı ortalama) yapın. Bu tek adım tahmin doğruluğunu dramatik şekilde artıracaktır.

```python
# Önerilen Ensemble Yaklaşımı
health_score_final = 0.6 * fuzzy_health + 0.4 * rf_predicted_health
```

---

### 2. CORS Güvenlik Açığı

`main.py` satır 48-54'te `allow_origins=["*"]` tüm domain'lere API erişimi açıyor.

```diff
 app.add_middleware(
     CORSMiddleware,
-    allow_origins=["*"],
+    allow_origins=[
+        "http://localhost:5173",   # Vite dev
+        "http://127.0.0.1:5173",
+        "https://yapisagligi.com", # Prod domain
+    ],
     allow_credentials=False,
```

---

### 3. 721 Satırlık Monolitik Backend

`main.py` tek dosyada **her şeyi** barındırıyor: API rotaları, Fuzzy Logic, ML modelleri, deprem haritası, korozyon hesaplamaları, Qwen3 entegrasyonu, CSV/Supabase kayıt. Bu sürdürülebilir değil.

**Önerilen Modüler Yapı:**

```
backend/
├── app.py                    # FastAPI init + CORS
├── config.py                 # Env vars, sabitler
├── models/
│   ├── schemas.py            # Pydantic modelleri
│   ├── fuzzy_engine.py       # Fuzzy Logic sistemi
│   ├── concrete_model.py     # Beton tahmin
│   └── risk_model.py         # RF risk modeli
├── services/
│   ├── earthquake.py         # Deprem haritası + zemin
│   ├── structural.py         # Yapısal skor hesaplama
│   ├── corrosion.py          # ASTM C876 hesaplama
│   ├── ai_comment.py         # Qwen3 LLM entegrasyonu
│   └── data_service.py       # Supabase + CSV kayıt
├── routes/
│   └── risk.py               # /api/risk-hesapla endpoint
└── data/
    └── earthquake_zones.json # Statik harita verileri
```

---

## 🟠 YÜKSEK ÖNCELİKLİ

### 4. Fuzzy Logic Kural Tabanı Yetersiz

Mevcut sistem sadece **5 kural** içeriyor (`main.py` satır 241-257). 3 giriş × 3 üyelik fonksiyonu = **27 olası kombinasyon** var, ancak bunların çoğu kapsanmıyor. Kapsanmayan girdi kombinasyonlarında Fuzzy motor `50.0` varsayılan değere düşüyor.

**Çözüm: Genişletilmiş Kural Matrisi**

| Beton | Korozyon | Yapısal Risk | → Sağlık |
|-------|----------|-------------|----------|
| Düşük | Yüksek | Yüksek | **Çok Kötü** |
| Düşük | Yüksek | Orta | **Çok Kötü** |
| Düşük | Orta | Yüksek | **Kötü** |
| Orta | Yüksek | Düşük | **Kötü** |
| Orta | Orta | Orta | **Orta** |
| Yüksek | Düşük | Orta | **İyi** |
| Yüksek | Düşük | Düşük | **Çok İyi** |
| ... | ... | ... | ... |

En az **15-20 kural** ile tüm anlamlı kombinasyonlar kapsanmalıdır.

---

### 5. AFAD Gerçek Zamanlı Tehlike Haritası Entegrasyonu

Deprem riski şu an `main.py` satır 343-425'te **80+ satırlık hardcoded Python dict** olarak tutuluyor. Bu statik, güncellenemiyor ve tüm ilçeleri kapsamıyor.

**Çözüm:**
- AFAD'ın **Türkiye Deprem Tehlike Haritası API**'sini entegre edin (https://tdth.afad.gov.tr)
- Koordinat bazlı sorgu ile o noktanın gerçek PGA (Peak Ground Acceleration) değerini alın
- Redis/memory cache ile aynı il-ilçe sorguları önbelleğe alın

```python
# Örnek: AFAD TDTH API Entegrasyonu
async def get_earthquake_hazard(lat: float, lon: float) -> dict:
    resp = await httpx.get(f"https://tdth.afad.gov.tr/api/hazard?lat={lat}&lon={lon}")
    return resp.json()  # PGA, SpectralAcceleration vb.
```

Bu tek özellik, projeyi **güncel AFAD verisiyle çalışan tek sivil araç** konumuna taşır.

---

### 6. Qwen3 LLM Çağrısı Senkron ve Kırılgan

`main.py` satır 166-211'de LLM çağrısı:
- **Senkron** `requests.post` ile yapılıyor (FastAPI async loop'u blokluyor)
- 120 saniye timeout, **retry yok**
- Ollama kapalıysa tüm API cevapsız kalıyor

**Çözüm:**
```python
import httpx

async def get_llm_comment_async(...):
    async with httpx.AsyncClient(timeout=60) as client:
        for attempt in range(3):  # 3 deneme
            try:
                resp = await client.post("http://localhost:11434/api/chat", ...)
                return resp.json()['message']['content']
            except Exception:
                if attempt == 2:
                    return "⚠️ AI yorumu şu an kullanılamıyor."
                await asyncio.sleep(2)
```

---

### 7. PDF Rapor Çıktısı

Kullanıcılar analiz sonucunu kaydetmek, paylaşmak ve arşivlemek isteyecek. Şu an hiçbir çıktı mekanizması yok.

**Çözüm:** `reportlab` veya `weasyprint` ile profesyonel PDF rapor oluşturun:
- Bina bilgileri tablosu
- Sağlık skoru göstergesi (gauge chart — matplotlib ile)
- Fuzzy Logic analiz detayları
- Korozyon ASTM C876 grafiği
- AI değerlendirme metni
- Yasal uyarı ve disclaimer
- QR kod ile rapor doğrulama

---

### 8. Rate Limiting ve API Güvenliği

Şu an API'ye sınırsız istek atılabilir. Bu hem LLM'i aşırı yükler hem de kötüye kullanıma açıktır.

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/risk-hesapla")
@limiter.limit("10/minute")  # IP başına dakikada 10 istek
async def risk_hesapla(req: RiskRequest, request: Request): ...
```

---

## 🟡 ORTA ÖNCELİKLİ / GELECEK VİZYONU

### 9. Yeni Parametre Önerileri (Risk Doğruluğunu Artıracak)

Mevcut giriş parametrelerine ek olarak şu parametrelerin eklenmesi modelin tahmin gücünü önemli ölçüde artıracaktır:

| Yeni Parametre | Bilimsel Dayanak | Uygulama Zorluğu |
|---------------|-----------------|------------------|
| **Karbonasyon derinliği (mm)** | Beton pH'ını düşürür, donatı korozyonunu tetikler | Orta |
| **Klorür konsantrasyonu (%)** | Denize yakın binalarda kritik | Orta |
| **Yapı malzemesi türü** (betonarme/yığma/çelik/karma) | Risk profili tamamen değişir | Kolay |
| **Bina toplam yüksekliği (m)** | Kat sayısından daha kesin; TBDY 2018 6.1 referansı | Kolay |
| **Güçlendirme yapılmış mı?** | Risk skorunu drastik düşürür | Kolay |
| **Donatı çapı ve aralığı** | Süneklik kapasitesini belirler | Zor |
| **Beton örtü kalınlığı (mm)** | Korozyon koruma düzeyi | Orta |
| **Son depremde hasar görmüş mü?** | Kümülatif hasar göstergesi | Kolay |

---

### 10. Görsel Çatlak Analizi (Bilgisayarlı Görü)

`crackPuan` parametresi formda var ama frontendde her zaman `0` gönderiliyor (`RiskForm.jsx` satır 72). Bu parametre aktive edilmeli.

**Gelecek Vizyon:** Kullanıcıdan fotoğraf yükleme alarak çatlak tespiti yapan bir **CNN (Convolutional Neural Network)** modeli entegre edilebilir:

```
Kullanıcı Fotoğraf Yükler → Edge Function ile Resize → 
CNN Model (crack/no-crack) → Sınıflandırma → crackPuan otomatik
```

Açık kaynak çatlak algılama veri setleri mevcut (SDNET2018, Crack500). Transfer learning ile MobileNetV2 kullanılarak hızlı bir model eğitilebilir.

---

### 11. İnteraktif Deprem Risk Haritası

Kullanıcının seçtiği il-ilçeyi harita üzerinde gösterin ve çevresi ile kıyaslayın:

```
Leaflet.js + OpenStreetMap
├── Deprem bölgesi renklendirme (kırmızı/sarı/yeşil)
├── Kullanıcının binasını pin ile işaretleme
├── Yakın tarihli deprem verileri (AFAD/Kandilli API)
└── Zemin sınıfı haritası overlay
```

---

### 12. Zaman Serisi / Yaşlanma Modeli

Binanın **zaman içinde nasıl bozulacağını** modelleyin:

```
Yapım Yılı: 1985 → Beton Yaşı: 41 yıl
├── Karbonasyon ilerleme hızı: ~1.2 mm/yıl (Tuutti modeli)  
├── Tahmini korozyon başlangıcı: 2010 (25 yıl sonra)
├── Mevcut beton mukavemeti kaybı: ~%15
└── 10 yıl sonra beklenen sağlık skoru: 42 → 35
```

Bu, kullanıcıya "binam gelecekte ne olacak?" sorusunun cevabını verir — **rakip hiçbir araçta yok.**

---

### 13. KVKK (Kişisel Verilerin Korunması) Uyumluluğu

Supabase'de saklanan `bina_analizleri` tablosu, dolaylı olarak kişisel veri içerebilir (il, ilçe, bina özellikleri kombinasyonu ile kişi tespit edilebilir).

**Gerekli Adımlar:**
1. **Veri anonimleştirme:** İl bazında aggregation, ilçe detayını hash'leme
2. **Kullanıcı rıza mekanizması:** Form başında "Verileriniz analiz amacıyla saklanacaktır" checkbox'ı
3. **Veri silme hakkı:** Supabase'de kullanıcının kendi verisini silme mekanizması
4. **Veri saklama süresi:** 90 gün sonra otomatik temizlik (Supabase cron job)

---

### 14. ResultCard.jsx Tailwind Sorunu

`ResultCard.jsx` Tailwind CSS sınıfları kullanıyor (`bg-card`, `rounded-2xl`, `text-gray-400` vb.) ancak projede Tailwind **yüklü ve konfigüre değil**. Bu bileşen görsel olarak tamamen kırık durumda.

**Çözüm:** Ya `legacy.css`'e uyumlu hale getirin ya da `App.jsx` inline stil kullanmaya devam edin. Şu an `App.jsx` içindeki inline sonuç gösterimi aktif, `ResultCard.jsx` ise import bile edilmiyor — bu ölü kod temizlenmeli.

---

### 15. Frontend: Sağlık Skoru Görselleştirme

Şu an skor sadece büyük bir sayı olarak gösteriliyor. Bunu **gauge chart** veya **radial progress** ile görselleştirmek güveni dramatik artırır:

```
      ╭───────────╮
     /    🟢 72    \
    /    ───────    \
   |   ╱        ╲   |
   |  ╱  SAĞLIK  ╲  |
   | ╱   SKORU    ╲ |
    ╲             ╱
     ╰───────────╯
   0    25   50   75  100
   🔴   🟠   🟡   🟢   🟢
```

React kütüphaneleri: `react-circular-progressbar`, `recharts`, veya custom SVG.

---

## 📊 Algoritmik İyileştirme Yol Haritası

```
Mevcut Sistem
  │
  ├─ Kısa Vade
  │    ├── risk_model.joblib Aktifleştir
  │    ├── Fuzzy Kuralları 5→20
  │    └── Ensemble: Fuzzy + RF
  │
  ├─ Orta Vade
  │    ├── ANFIS Entegrasyonu
  │    ├── XGBoost/LightGBM Ekleme
  │    └── AFAD API Bağlantısı
  │
  └─ Uzun Vade
       ├── CNN Çatlak Analizi
       ├── Zaman Serisi Modeli
       └── Federated Learning
```

---

## 🔧 sentetik_veri_uret.py Hatası

> **UYARI:** `sentetik_veri_uret.py` satır 24'te `genel_risk_seviyesi` fonksiyonu `main.py`'den import ediliyor ancak **bu fonksiyon main.py'de tanımlı değil**. Bu script çalıştırıldığında `ImportError` verecektir.

---

## 📈 4 Kişilik Ekip İçin Sprint Planı

| Sprint | Hafta | Görevler | Atanacak Kişi |
|--------|-------|----------|---------------|
| **S1** | 1-2 | CORS fix, monolith ayrıştırma | Backend Dev |
| **S1** | 1-2 | ResultCard.jsx temizliği, gauge chart | Frontend Dev |
| **S2** | 3-4 | risk_model aktifleştirme, ensemble | ML/Data Eng |
| **S2** | 3-4 | Fuzzy kural genişleme (5→20) | Backend Dev |
| **S3** | 5-6 | AFAD API entegrasyonu, PDF rapor | Backend Dev |
| **S3** | 5-6 | İnteraktif harita, form wizard | Frontend Dev |
| **S4** | 7-8 | KVKK compliance, rate limiting | Full-stack |
| **S4** | 7-8 | ANFIS entegrasyonu, yeni parametreler | ML/Data Eng |

---

## Sonuç

Bu proje **doğru problemi, doğru teknolojilerle** çözmeye başlamış. Ancak şu an:
- Eğitilen modellerin %66'sı **kullanılmıyor** (risk_model + ANFIS)
- Fuzzy Logic sadece **5 kuralla** çalışıyor (yetersiz kapsam)
- Frontend'de **ölü kod** var (ResultCard.jsx)

Bu rapordaki önerilerin **sadece kritik olanları** (Sprint 1-2) bile uygulandığında, sistem hem teknik doğruluk hem de güvenilirlik açısından **tamamen farklı bir seviyeye** ulaşacaktır.

> Bu rapor, projenin derin teknik analizine dayalı, mevcut kod tabanındaki spesifik fırsatlara odaklanmış stratejik bir yol haritasıdır.
