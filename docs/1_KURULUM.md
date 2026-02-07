# 🚀 V12 Titanium - Proje Kurulum Rehberi

Bu rehber, projeye yeni katılan takım arkadaşlarının (veya kurulumu tekrar yapmak isteyenlerin) projeyi sıfırdan bilgisayarlarına kurmaları içindir.

---

## 🤔 ÖNCE BUNU OKU: NEDEN BU SİSTEM?

**CI/CD (Sürekli Entegrasyon), takım halinde çalışmanın anahtarıdır.**

### ❌ ESKİ USUL (Sorunlu):
- "Bende çalışıyor, sende niye çalışmıyor?"
- "Hangi dosya en güncel?"
- "Emine kütüphane eklemiş, haberim yok!"
**Sonuç:** Kaos ve zaman kaybı. 📉

### ✅ BİZİM SİSTEM (Antigravity & GitHub Actions):
- Herkes **tek komutla** güncel dosyaları alır.
- Gönderilen her kod **otomatik testten** geçer.
- Hatalar anında yakalanır.
**Sonuç:** Hız ve güven. 🚀

---

## 📋 PRE-REQUISITES (GEREKLİLİKLER)

Bilgisayarında şunlar yüklü olmalı:
- ✅ **Windows 10/11**
- ✅ **Python 3.11** (python.org'dan indir, "Add to PATH" işaretle!)
- ✅ **Git** (git-scm.com'dan indir)
- ✅ **Antigravity** (antigravity.dev'den indir)

---

## 🛠️ ADIM ADIM KURULUM

Her adımı sırasıyla yap. PowerShell kullanacağız.

### ADIM 1: PowerShell Aç
1. Windows tuşuna bas, "PowerShell" yaz.
2. "Windows PowerShell" uygulamasını aç.

### ADIM 2: Masaüstüne Git
```powershell
cd Desktop
```

### ADIM 3: Projeyi İndir
```powershell
git clone https://github.com/cagriaksoy191-oss/structural_health.git
```
*(Bu işlem 1-2 dakika sürebilir)*

### ADIM 4: Proje Klasörüne Gir
```powershell
cd structural_health
```

### ADIM 5: Sanal Ortam (venv) Kur
Bu, projenin kütüphanelerini bilgisayarındaki diğer projelerden ayırır.
```powershell
python -m venv venv
```

### ADIM 6: Sanal Ortamı Aktifleştir
```powershell
.\venv\Scripts\Activate
```
✅ Satır başında `(venv)` yazısı görmelisin.

### ADIM 7: Kütüphaneleri Yükle
```powershell
pip install -r requirements.txt
```
*(Bu işlem 2-5 dakika sürebilir)*

### ADIM 8: Projeyi Test Et
Sunucuyu çalıştırıp her şeyin yolunda olduğunu görelim:
```powershell
py -3.11 main.py
```
Tarayıcıda `http://127.0.0.1:8000` adresine git. Site açılıyorsa tamamdır! (Durdurmak için Ctrl+C)

### ADIM 9: Antigravity ile Aç
1. **Antigravity** uygulamasını aç.
2. `File → Open Folder` menüsünden masaüstündeki `structural_health` klasörünü seç.

---

## 🎉 TEBRİKLER! ARTIK HAZIRSIN.

Şimdi **`2_CALISMA_REHBERI.md`** dosyasını okuyarak nasıl çalışacağını öğren.

---

### 🆘 HATA MI ALDIN?

| Hata | Çözüm |
|------|-------|
| `python bulunamadı` | Python'u yeniden yükle, "Add to PATH" seçeneğini UNUTMA. |
| `git bulunamadı` | Git'i yükle ve bilgisayarı yeniden başlat. |
| `(venv) gelmiyor` | PowerShell'i yönetici olarak açıp `Set-ExecutionPolicy RemoteSigned` yapabilirsin. |
| `pip install hatası` | İnternet bağlantını kontrol et. |

*Son Güncelleme: 7 Şubat 2026*
