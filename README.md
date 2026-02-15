# 🚀 V12 Titanium - Proje Kullanım Kılavuzu

Merhaba ekip! 👇 Projeyi kendi bilgisayarınızda çalıştırmak için bu adımları takip edin.

---

## 🛠️ İlk Kurulum (Sadece 1 Kez - Projeyi İlk İndirdiğinde)

1.  **Projeyi GitHub'dan indir:**
    ```bash
    git clone https://github.com/cagriaksoy191-oss/structural_health.git
    ```

2.  **Proje klasörüne gir:**
    ```bash
    cd structural_health
    ```

3.  **Sanal Ortam (Venv) oluştur:**
    ```bash
    python -m venv venv
    ```

4.  **Sanal Ortamı aktif et:**
    ```bash
    .\venv\Scripts\activate
    ```
    ✅ Başında **`(venv)`** yazısı çıkmalı.

5.  **Kütüphaneleri yükle:**
    ```bash
    pip install -r requirements.txt
    ```

6.  **Gizli Anahtar Dosyasını Oluştur:**
    *   Proje klasöründe sağ tık → Yeni Metin Belgesi oluştur.
    *   Adını **`.env`** yap (sonunda `.txt` kalmasın!).
    *   Çağrı'nın size özelden attığı **SUPABASE_URL** ve **SUPABASE_KEY** satırlarını içine yapıştırıp kaydedin.

---

## 🟢 Günlük Kullanım (Her Gün - Bilgisayarı Her Açtığında)

**En kolay yol:** Proje klasörüne girip **`baslat.bat`** dosyasına çift tıklayın. Her şeyi otomatik yapar! ✅

**Veya CMD ile manuel:**

1.  Proje klasörüne gidin:
    ```bash
    cd "proje_klasor_yolunuz"
    ```

2.  Sanal ortamı aktif edin:
    ```bash
    .\venv\Scripts\activate
    ```

3.  Projeyi çalıştırın:
    ```bash
    uvicorn main:app --reload
    ```
    ✅ **"Application startup complete"** yazısı görünce hazır!

---

## 🌙 Gün Sonu Rutini (Kod Değiştirdiyseniz - İş Bitince)

Kodlarda değişiklik yaptıysanız, günün sonunda mutlaka şunu çalıştırın:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\gunsonu.ps1
```

**Ne İşe Yarar?** Kodlarınızı güvenli şekilde GitHub'a gönderir (yedekler + CI/CD tetikler).

---

## ❓ Sıkça Sorulan Sorular

*   **S:** "Module not found" hatası alıyorum?
    *   **C:** `.\venv\Scripts\activate` komutunu unuttun. Önce onu yap, sonra tekrar dene.

*   **S:** Swagger UI / Site açılmıyor?
    *   **C:** CMD penceresini (siyah ekranı) kapattın mı? O hep açık kalmalı.

*   **S:** Veriler nereye gidiyor?
    *   **C:** Hepsi buluttaki (Supabase) ortak veritabanımıza gidiyor. Herkes sonuçları orada görebilir.

*   **S:** `.env` dosyası nedir?
    *   **C:** Supabase bağlantı anahtarları. Bu dosyayı Çağrı size özelden atacak. GitHub'a gitmez, güvenlidir.
