# 🚀 V12 Titanium - Takım Arkadaşları Kurulum Rehberi
## Emine, Talha ve Baha İçin Adım Adım Anlatım

---

# 🤔 ÖNCE BUNU OKU: CI/CD NE İŞİMİZE YARAR?

## Basit Anlatım

**CI/CD = Otomatik Test Robotu** 🤖

Düşün ki bir ödev yapıyorsun. Her değişiklik yaptığında hoca gelip "doğru mu yanlış mı?" diye kontrol ediyor. İşte CI/CD tam olarak bu!

## Gerçek Hayattan Örnek

### ❌ CI/CD OLMADAN (Eski Usul):
```
1. Emine kod yazar, çalışıyor der
2. Talha çeker, ÇALIŞMIYOR! 😱
3. Talha: "Emine bu ne ya çalışmıyor!"
4. Emine: "Bende çalışıyordu ya!"
5. 2 saat hata aranır...
6. Sonunda: Emine bir kütüphane yüklemeyi unutmuş 🤦
```

### ✅ CI/CD İLE (Bizim Sistem):
```
1. Emine kod yazar, push yapar
2. 30 saniye sonra GitHub'dan bildirim: ❌ TEST BAŞARISIZ!
3. Emine hemen görür: "Ha, kütüphane eksik"
4. Düzeltir, tekrar push yapar
5. GitHub: ✅ TEST BAŞARILI!
6. Artık Talha çektiğinde sorunsuz çalışır 🎉
```

## Bize Ne Katıyor?

| Avantaj | Açıklama |
|---------|----------|
| 🐛 **Erken Hata Tespiti** | Hata 5 dakikada bulunur, 5 saatte değil |
| 👥 **Takım Uyumu** | "Bende çalışıyor" tartışması biter |
| 📋 **Profesyonellik** | Gerçek şirketler böyle çalışır, CV'ye yazarsın |
| 🛡️ **Güvenlik** | Bozuk kod ana projeye karışmaz |

---

# 📋 KURULUM ADIMLARI

## 👤 SEN KİMSİN?

**Eğer Çağrı isen:** Bu rehberi zaten biliyorsun, sen kurdun! 😎

**Eğer Emine, Talha veya Baha isen:** Aşağıdaki adımları sırasıyla yap. Her adımı tamamla, sonra diğerine geç.

---

# ADIM 1: GitHub Davetini Kabul Et ✉️

## Ne Yapacaksın?
Çağrı sana e-posta ile davet gönderdi. Bunu kabul etmen lazım.

## Adımlar:
1. **E-postanı aç** (GitHub'a kayıtlı olan)
2. **"You've been invited..."** başlıklı maili bul
3. **Yeşil butona tıkla:** "Accept invitation"
4. **Giriş yap** (GitHub hesabınla)

## ✅ Kontrol:
- https://github.com/cagriaksoy191-oss/structural_health adresine git
- Sayfayı görebiliyorsan → TAMAM! ✅
- "404 Not Found" görüyorsan → Daveti kabul etmemişsin, e-postanı kontrol et

---

# ADIM 2: Projeyi Bilgisayarına İndir 📥

## Ne Yapacaksın?
GitHub'daki projeyi kendi bilgisayarına kopyalayacaksın.

## Adımlar:

### 2.1 Klasör Oluştur
```
1. Bilgisayarında C: diskine git
2. "Projects" adında yeni klasör oluştur
   (Yol: C:\Projects olacak)
```

### 2.2 Terminal Aç
```
1. Windows tuşuna bas
2. "PowerShell" yaz
3. "Windows PowerShell" uygulamasını aç
```

### 2.3 Komutları Çalıştır
Terminale şunları SIRAYLA yaz (her birinden sonra Enter bas):

```powershell
cd C:\Projects
```
```powershell
git clone https://github.com/cagriaksoy191-oss/structural_health.git
```
```powershell
cd structural_health
```

## ✅ Kontrol:
```powershell
dir
```
yazınca `main.py`, `index.html` gibi dosyaları görüyorsan → TAMAM! ✅

---

# ADIM 3: Python Kur 🐍

## Ne Yapacaksın?
Projemiz Python ile çalışıyor. Python 3.11 lazım.

## Adımlar:

### 3.1 Python Var mı Kontrol Et
Terminale yaz:
```powershell
py --version
```
- "Python 3.11.x" yazıyorsa → ADIM 3.2'yi ATLA, ADIM 3.3'e geç
- Hata veriyorsa → ADIM 3.2'yi yap

### 3.2 Python İndir ve Kur
1. https://www.python.org/downloads/ adresine git
2. "Download Python 3.11.x" butonuna tıkla
3. İndirilen dosyayı çalıştır
4. ⚠️ **ÖNEMLİ:** "Add Python to PATH" kutusunu İŞARETLE!
5. "Install Now" tıkla
6. Bilgisayarı YENIDEN BAŞLAT

### 3.3 Sanal Ortam Oluştur
Terminale şunları SIRAYLA yaz:

```powershell
cd C:\Projects\structural_health
```
```powershell
py -3.11 -m venv venv
```
```powershell
.\venv\Scripts\Activate
```

Terminalin başında `(venv)` yazısı görünecek. Bu doğru demek!

### 3.4 Kütüphaneleri Yükle
```powershell
pip install -r requirements.txt
```
Bu 2-3 dakika sürebilir, bekle.

## ✅ Kontrol:
```powershell
py -3.11 -c "import pandas; print('OK')"
```
"OK" yazıyorsa → TAMAM! ✅

---

# ADIM 4: Ollama Kur (Yapay Zeka İçin) 🤖

## Ne Yapacaksın?
Projemiz yerel yapay zeka kullanıyor. Bunun için Ollama lazım.

## Adımlar:

### 4.1 Ollama İndir
1. https://ollama.ai adresine git
2. "Download" butonuna tıkla
3. Windows sürümünü indir
4. İndirilen dosyayı çalıştır ve kur

### 4.2 Qwen Modelini İndir
YENİ bir PowerShell penceresi aç ve yaz:
```powershell
ollama pull qwen3:8b
```
⚠️ Bu 5-10 GB indirecek! İnternet hızına göre 10-30 dakika sürebilir.

### 4.3 Test Et
```powershell
ollama list
```
"qwen3:8b" görünüyorsa → TAMAM! ✅

---

# ADIM 5: Model Dosyalarını Al 📁

## Ne Yapacaksın?
Bazı dosyalar çok büyük olduğu için GitHub'da yok. Çağrı'dan alman lazım.

## İhtiyacın Olan Dosyalar:
```
concrete_model.joblib      (4 MB)
risk_model.joblib          (8 MB)
anfis_model_agirliklari.pth
```

## Nasıl Alacaksın?
- **Seçenek 1:** Çağrı USB ile verir
- **Seçenek 2:** Google Drive/Dropbox linki ister
- **Seçenek 3:** WhatsApp'tan ister

## Nereye Koyacaksın?
Bu dosyaları `C:\Projects\structural_health` klasörüne kopyala.
(Yani main.py ile aynı yere)

## ✅ Kontrol:
```powershell
cd C:\Projects\structural_health
dir *.joblib
```
`concrete_model.joblib` ve `risk_model.joblib` görünüyorsa → TAMAM! ✅

---

# ADIM 6: Self-Hosted Runner Kur 🏃

## Ne Yapacaksın?
Bu, GitHub'dan test komutlarını alan program. Push yaptığında kendi bilgisayarında test çalışır.

## ⚠️ ÖNEMLİ:
Her kişi KENDİ runner'ını kurar. Böylece:
- Emine push yapınca → Emine'nin bilgisayarı test çalıştırır
- Talha push yapınca → Talha'nın bilgisayarı test çalıştırır
- Kimse kimsenin bilgisayarını kullanmaz!

## Adımlar:

### 6.1 GitHub'dan Token Al
1. https://github.com/cagriaksoy191-oss/structural_health/settings/actions/runners/new adresine git
2. "Windows" seçeneğini tıkla
3. Sayfadaki komutları GÖR (aşağıda açıklıyorum)

### 6.2 Runner Klasörü Oluştur
PowerShell'de:
```powershell
mkdir C:\actions-runner
cd C:\actions-runner
```

### 6.3 Runner'ı İndir
GitHub sayfasındaki "Download" bölümündeki komutu kopyala-yapıştır.
Genelde şuna benzer:
```powershell
Invoke-WebRequest -Uri https://github.com/actions/runner/releases/download/v2.XXX.X/actions-runner-win-x64-2.XXX.X.zip -OutFile actions-runner.zip
```
(XXX.X kısmı değişebilir, GitHub'daki güncel halini kullan!)

### 6.4 Zip'i Aç
```powershell
Expand-Archive -Path actions-runner.zip -DestinationPath .
```

### 6.5 Yapılandır
GitHub sayfasındaki "Configure" bölümündeki komutu kopyala-yapıştır.
Genelde şuna benzer:
```powershell
.\config.cmd --url https://github.com/cagriaksoy191-oss/structural_health --token BURAYA_GITHUB_TOKEN_GELECEK
```

Sana birkaç soru soracak:
- **Runner name:** Kendi adını yaz! 
  - Emine → `emine-pc`
  - Talha → `talha-pc`
  - Baha → `baha-pc`
- Diğer sorulara **Enter** basarak geç (varsayılan değerler OK)

### 6.6 Runner'ı Başlat
```powershell
.\run.cmd
```

Şunu görmelisin:
```
√ Connected to GitHub
Listening for Jobs
```

## ✅ Kontrol:
- https://github.com/cagriaksoy191-oss/structural_health/settings/actions/runners adresine git
- Kendi runner'ını "Idle" (boşta) olarak görüyorsan → TAMAM! ✅

---

# ADIM 7: Her Şeyi Test Et ✅

## 7.1 Backend Sunucuyu Başlat
YENİ bir PowerShell aç:
```powershell
cd C:\Projects\structural_health
.\venv\Scripts\Activate
py -3.11 main.py
```
"Uvicorn running on http://127.0.0.1:8000" görmelisin.

## 7.2 Health Check Çalıştır
BAŞKA BİR PowerShell aç:
```powershell
cd C:\Projects\structural_health
.\venv\Scripts\Activate
py -3.11 tests/health_check.py
```
"TÜM KRİTİK KONTROLLER BAŞARILI" görmelisin.

## 7.3 Web Arayüzünü Test Et
1. Dosya Gezgini'nde `C:\Projects\structural_health` klasörüne git
2. `index.html` dosyasına çift tıkla (tarayıcıda açılır)
3. Formu doldur ve "Risk Skorunu Hesapla" butonuna bas
4. Sonuç geliyorsa → HER ŞEY TAMAM! 🎉

---

# � GÜNLÜK KULLANIM

## Her Gün Şunları Yap:

### 1. Son Değişiklikleri Çek (Sabah)
```powershell
cd C:\Projects\structural_health
git pull origin main
```

### 2. Kodunu Yaz
Normal şekilde çalış, istediğin değişikliği yap.

### 3. Değişiklikleri Kaydet ve Gönder
```powershell
git add .
git commit -m "Ne yaptığını kısaca yaz"
git push origin main
```

### 4. Sonucu Bekle
- 30-60 saniye bekle
- GitHub Actions sayfasını kontrol et
- ✅ Yeşil tik = Her şey OK
- ❌ Kırmızı X = Bir sorun var, logları oku

---

# ❓ SIKÇA KARŞILAŞILAN SORUNLAR

## "git: command not found" hatası
→ Git yüklü değil.
→ https://git-scm.com/download/win adresinden indir ve kur.

## "Permission denied" hatası
→ GitHub davetini kabul etmemişsin.
→ E-postanı kontrol et.

## "Model bulunamadı" hatası
→ .joblib dosyaları eksik.
→ Çağrı'dan USB ile al.

## "Ollama bağlantı hatası"
→ Ollama çalışmıyor.
→ Başlat menüsünden "Ollama" uygulamasını aç.

## "Runner offline görünüyor"
→ Runner kapalı.
→ `C:\actions-runner\run.cmd` çalıştır.

## "Push rejected" hatası
→ Önce pull yapman lazım.
→ `git pull origin main` yaz, sonra tekrar push yap.

---

# 📱 YARDIM LAZIMSA

1. **Önce bu rehberi tekrar oku** �
2. **Hata mesajını Google'a yaz** 🔍
3. **ChatGPT'ye sor** 🤖
4. **Grup sohbetine yaz** 💬
5. **En son Çağrı'yı ara** 📞

---

# 📊 ÖZET TABLO

| Adım | Ne Yaptın? | Kontrol |
|------|------------|---------|
| 1 | GitHub daveti | Repo sayfası açılıyor mu? |
| 2 | Projeyi klonla | `dir` ile dosyalar görünüyor mu? |
| 3 | Python kur | `py --version` çalışıyor mu? |
| 4 | Ollama kur | `ollama list` çalışıyor mu? |
| 5 | Model dosyaları | .joblib dosyaları var mı? |
| 6 | Runner kur | GitHub'da "Idle" görünüyor mu? |
| 7 | Test et | Web arayüzü çalışıyor mu? |

**7'si de ✅ ise: SEN HAZIRSIN!** 🎉

---

*Son Güncelleme: 4 Şubat 2026*
*Hazırlayan: Çağrı*
*Takım: Çağrı, Emine, Talha, Baha*
