# 🚀 V12 Titanium - Takım Arkadaşı Kurulum Rehberi

Bu rehber, projeye sıfırdan katılacak arkadaşlar için hazırlanmıştır.
Tüm adımları sırayla takip et, atladığın adım olmasın!

---

## 📋 KURULUM ÖNCESİ GEREKLİLİKLER

Bilgisayarında şunlar yüklü olmalı:
- ✅ Windows 10/11
- ✅ Python 3.11 (python.org'dan indir)
- ✅ Git (git-scm.com'dan indir)
- ✅ VS Code (code.visualstudio.com'dan indir)

---

# ADIM 1: PowerShell Aç

1. Windows tuşuna bas
2. "PowerShell" yaz
3. "Windows PowerShell" uygulamasını aç

**Bundan sonraki tüm komutlar bu PowerShell penceresine yazılacak!**

---

# ADIM 2: Masaüstüne Git

Aşağıdaki komutu PowerShell'e yapıştır ve **Enter** tuşuna bas:

```powershell
cd Desktop
```

**Beklenen sonuç:** Hiçbir hata mesajı yok, sadece yeni satır açılır.

---

# ADIM 3: Projeyi GitHub'dan İndir

Aşağıdaki komutu **tek seferde** kopyala ve PowerShell'e yapıştır, **Enter** bas:

```powershell
git clone https://github.com/cagriaksoy191-oss/structural_health.git
```

**Beklenen sonuç:**
```
Cloning into 'structural_health'...
remote: Enumerating objects: ...
Resolving deltas: 100% ... done.
```

⏱️ Bu işlem 1-2 dakika sürebilir, bekle.

---

# ADIM 4: Proje Klasörüne Gir

Aşağıdaki komutu yapıştır ve **Enter** bas:

```powershell
cd structural_health
```

**Beklenen sonuç:** Komut satırı şu şekilde değişir:
```
PS C:\Users\SENİN_ADIN\Desktop\structural_health>
```

---

# ADIM 5: Sanal Ortam Oluştur (venv)

Aşağıdaki komutu yapıştır ve **Enter** bas:

```powershell
python -m venv venv
```

**Beklenen sonuç:** Hiçbir çıktı yok, sessizce biter (10-30 saniye sürer).

⚠️ **Hata alırsan:** `python` yerine `py -3.11 -m venv venv` dene.

---

# ADIM 6: Sanal Ortamı Aktifleştir

Aşağıdaki komutu yapıştır ve **Enter** bas:

```powershell
.\venv\Scripts\Activate
```

**Beklenen sonuç:** Satır başında `(venv)` yazısı belirir:
```
(venv) PS C:\Users\SENİN_ADIN\Desktop\structural_health>
```

✅ **(venv) yazısını gördüysen devam et!**

---

# ADIM 7: Kütüphaneleri Yükle

Aşağıdaki komutu yapıştır ve **Enter** bas:

```powershell
pip install -r requirements.txt
```

**Beklenen sonuç:**
```
Collecting fastapi
Collecting uvicorn
...
Successfully installed ...
```

⏱️ Bu işlem 2-5 dakika sürebilir. "Successfully installed" yazısını görene kadar bekle.

---

# ADIM 8: Projeyi Test Et

Aşağıdaki komutu yapıştır ve **Enter** bas:

```powershell
py -3.11 main.py
```

**Beklenen sonuç:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Started server process
```

Şimdi:
1. Tarayıcını aç (Chrome/Edge/Firefox)
2. Adres çubuğuna yaz: `http://127.0.0.1:8000`
3. Form sayfasını gör
4. Bir kaç veri girerek "Risk Skorunu Hesapla" butonuna bas
5. AI cevabı gelirse **kurulum başarılı!** ✅

**Sunucuyu durdurmak için:** PowerShell'de `Ctrl+C` bas.

---

# ADIM 9: Antigravity Kur

1. **VS Code**'u aç
2. Sol tarafta **Extensions** (4 kare ikon) tıkla veya `Ctrl+Shift+X` bas
3. Arama kutusuna **"Antigravity"** yaz
4. **"Antigravity"** eklentisini bul ve **Install** butonuna bas
5. VS Code'u kapat ve yeniden aç

---

# ADIM 10: Projeyi Antigravity ile Aç

1. VS Code (Antigravity) aç
2. `File → Open Folder` tıkla
3. Masaüstündeki `structural_health` klasörünü seç
4. "Open" butonuna bas

---

# ✅ KURULUM TAMAMLANDI!

Artık her akşam şu komutu Antigravity'e yazabilirsin:

> **"Runner'ı kontrol et, arkadaşlarımın değişikliklerini çek, çakışma varsa her iki tarafın en iyi kısımlarını birleştir ve neden bu kararı verdiğini açıkla, sonra benim değişikliklerimi GitHub'a gönder, CI/CD testini bekle ve projeyi tarayıcıda test edip sonucu göster"**

---

## 🔧 HER GÜN NE YAPACAKSIN?

| Zaman | Yapılacak İş |
|-------|-------------|
| **Sabah** | Antigravity'i aç, kod yazmaya başla |
| **Gün boyu** | İstediğin gibi geliştir |
| **Akşam** | Yukarıdaki komutu Antigravity'e yaz |
| **Sonra** | Gönül rahatlığıyla bilgisayarı kapat |

---

## ❓ SIKÇA SORULAN SORULAR

**S: Her gün venv oluşturmam gerekiyor mu?**
C: Hayır! Sadece 1 kere, kurulumda.

**S: Her gün pip install yapmam gerekiyor mu?**
C: Hayır! Sadece 1 kere, kurulumda.

**S: Projeyi her seferinde GitHub'dan indirmem gerekiyor mu?**
C: Hayır! 1 kere indiriyorsun, sihirli komut zaten güncelliyor.

**S: Runner'ı ben mi açacağım?**
C: Hayır! Runner sadece Çağrı'nın bilgisayarında. Senin yapman gereken bir şey yok.

**S: (venv) yazısı kayboldu, ne yapayım?**
C: `.\venv\Scripts\Activate` komutunu tekrar yaz.

---

## 🆘 HATA DURUMUNDA

| Hata | Çözüm |
|------|-------|
| `python bulunamadı` | Python'u yeniden yükle, PATH'e ekle |
| `git bulunamadı` | Git'i yeniden yükle |
| `pip install hata verdi` | İnterneti kontrol et, tekrar dene |
| `main.py çalışmadı` | venv aktif mi kontrol et |

Çözemezsen Çağrı'ya yaz!

---

*Son Güncelleme: 7 Şubat 2026*
