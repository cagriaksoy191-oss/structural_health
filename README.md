# Yapı Sağlığı Ön Tarama Sistemi

Bu proje, yapısal sağlık taraması yapmak üzere geliştirilmiş, makine öğrenmesi ve bulanık mantık (v2 fuzzy logic) tabanlı bir web aracıdır.

## ⚙️ Sistem Mimarisi ve Temel Özellikler

Sistem, 6 aşamalı bir analiz pipeline'ından oluşmaktadır:
*   **AFAD Hybrid Deprem Verisi:** AFAD Event API entegrasyonu (başarısızlık durumunda statik harita fallback desteği).
*   **Yapısal Skor:** TBDY uyumlu 14 ayrı kritere göre yapısal risk hesaplaması.
*   **Beton Dayanım Tahmini:** Random Forest tabanlı makine öğrenmesi modeli ile (UPV ve Rebound).
*   **Korozyon Analizi:** ASTM C876 standardına göre sürekli interpolasyon.
*   **Karar Motoru:** Yüksek doğruluklu `v2_fuzzy27` bulanık mantık motoru ve kısıtlayıcı politika katmanı (Policy Layer).
*   **AI Uzman Yorumu:** Ollama ve Qwen3:8b büyük dil modeli ile veriye dayalı Türkçe yorum.

## 📋 Gereksinimler (Prerequisites)

*   **Zorunlu:** 
    *   Python 3.x
    *   Node.js (Frontend bağımlılıkları için zorunlu)
    *   Git
*   **İsteğe Bağlı (AI Yorum Özelliği İçin):** 
    *   Ollama ortamı ve `qwen3:8b` modeli. 
    *   *Not:* Ollama kapalıysa veya eksikse sistem çökmeyecektir; sadece yapay zeka yorum özelliği uyarı dönecektir.

## 🚀 Hızlı Başlangıç (Happy Path)

Sistemi Windows ortamında en hızlı şekilde kurmak ve başlatmak için aşağıdaki adımları sırasıyla izleyin:

1.  **Projeyi Klonlayın:**
    ```bash
    git clone https://github.com/cagriaksoy191-oss/structural_health.git
    cd structural_health
    ```

2.  **Ortam Değişkenlerini (Konfigürasyon) Edin:**
    *   Güvenlik politikası gereği repoda `.env.example` yoktur.
    *   Sistem yetkilisinden anahtar listesini isteyip kök dizine `.env` dosyası oluşturarak kaydedin. 
    *   *(Uyarı: Elinizde `.env` dosyası (örn. Supabase bağlantısı) yoksa endişelenmeyin! Sistem tamamen çökmez, veritabanı entegrasyonu olmadan "CSV" yedek modunda sınırlı çalışmaya devam eder).*

3.  **Otomatik Kurulum:**
    Aşağıdaki dosyaya çift tıklayın veya çağırın. Bu betik Python paketlerini (`pip`) ve Frontend paketlerini (`npm`) sizin yerinize kuracaktır.
    ```bash
    kurulum.bat
    ```

4.  **Projeyi Başlatma:**
    Aşağıdaki dosyaya çift tıklayın. Backend ve Frontend sunucularınız otomatik açılacaktır.
    ```bash
    baslat.bat
    ```

## 🔐 .env Konfigürasyon Detayları

Eğitim veya geliştirme için `.env` dosyanızda olması beklenen temel (ancak tamamen zorunlu olmayan) değişkenler şunlardır:
*   `SUPABASE_URL` ve `SUPABASE_KEY`: Veritabanı entegrasyonu için.
*   `ALLOWED_ORIGINS` (Opsiyonel): CORS kabul listesi.
*   `AFAD_TIMEOUT` ve `AFAD_CACHE_TTL` (Opsiyonel): Deprem API limitleri.
*   `PINECONE_API_KEY`: Sadece takım içi akıllı senkronizasyon scripti (`/gunsonu`) için.

## 🛠️ Manuel Başlatma ve Hata Ayıklama (İleri Düzey)

Eğer `baslat.bat` kullanmak istemiyorsanız sistemi manuel olarak başlatabilirsiniz. **Uyarı:** İşletim sistemindeki "global" Python yorumlayıcısını (interpreter) tetiklememek için mutlaka sanal ortamınızı (`.venv` veya `venv`) aktif etmelisiniz.

1.  **Backend'i başlat:**
    Aşağıdaki komutlardan sizin kurulumunuza uyan dizini aktif edip projeyi başlatabilirsiniz:
    ```bash
    # Eğer .venv klasörü oluşmuşsa:
    .\.venv\Scripts\activate
    
    # Veya venv klasörü oluşmuşsa:
    .\venv\Scripts\activate
    
    # Ortam aktifleşince projeyi başlat:
    python main.py
    ```
    *Backend `http://127.0.0.1:8000` portunda açılacaktır.*

2.  **Frontend'i başlat (Ayrı bir terminalde):**
    ```bash
    cd frontend
    npm run dev
    ```
    *Frontend arayüzü `http://localhost:5173` portunda hizmet verecektir.*

## 🔌 API Özeti

Sistem ağırlıklı olarak tek bir endpoint üzerinden hizmet sunar:
*   **POST** `/api/risk-hesapla` (Backend Port: 8000)
    *   Girdi: JSON formatında yapı, deprem ve tahribatsız test verileri (`RiskRequest`).
    *   Çıktı: Skorlar, fuzzy explainability trace, korozyon sonucu ve AI yorumu (`RiskResponse`).

## 🧪 Test ve Doğrulama
Kod tabanı testlerle korunmaktadır. Hızlı validasyon ve kalite kontrolü için:
*   Uçtan uca API Sağlaması (Smoke Test): Repoda yerleşik bulunan `python tests/health_check.py` dosyasını çalıştırıp sisteminizin genel sağlığını ek bağımlılık kurmadan anında test edebilirsiniz.
*   Birim Testleri (Geliştirme Ortamı): Eğer ortamınıza kendiniz `pytest` kütüphanesini kurduysanız (varsayılan sürüm gereksinimlerinde zorunlu gelmez), `pytest tests/` komutuyla kapsamlı testleri koşturabilirsiniz.

## 🤖 Takım İçi İş Akışları (Opsiyonel / Sınırlı)

Ekip için tasarlanmış iki özel PowerShell betiği bulunmaktadır:
*   **`/sabah` (`scripts/sabah_rutini.ps1`):** Güne başlarken kod senkronizasyonu ve paket hash eşleşmesi yapar. Şu anda yalnızca standart `venv` klasör yapısıyla uyumludur.
*   **`/gunsonu` (`scripts/gunsonu.ps1`):** Gün bitiminde güvenli commit, çakışma testleri ve Pinecone MCP hafıza senkronizasyonunu yönetir. 

## 📌 Bilinen Sınırlamalar / Notlar

*   **LLM Bağımlılığı:** Ollama ortamı yoksa API işlemleri hata (crash) vermez, sadece "AI Yorum" alanı için opsiyonel uyarı metni oluşturur.
*   **İzolasyon:** Bu repoda kurulu bir Docker veya Devcontainer mekanizması bulunmamaktadır; doğrudan Windows native ortam (bat/ps1) baz alınmıştır.
*   **Sabah Scripti:** Yukarıda değinildiği gibi `/sabah` akışı henüz `.venv` dizinine değil, daha çok `venv` dizin yapısına göre kontrol sağlar.

## 📚 Geliştirme Referansı (AGENTS.md)

Bu README.md operasyonel bir giriş dokümanıdır. Sistemin iç kuralları, tasarım kararları (v2 fuzzy matrisi vb.) detaylı olarak repo içindeki **`AGENTS.md`** belgesinde incelenebilir. 

**Önemli Uyarı:** Kod tabanı (`*.py`, `*.js`, `*.ps1`, `*.bat`) her zaman birinci derece doğruluk kaynağıdır. AGENTS.md veya bu README dosyası ile yazılımın davranışları arasında bir çelişki görülürse, scriptlerin/kodun aktif davranışı esas alınmalıdır.
