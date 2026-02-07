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
1. Emine kod yazar, "/gonder" der
2. 30 saniye sonra Antigravity: ❌ TEST BAŞARISIZ!
3. Emine hemen görür: "Ha, kütüphane eksik"
4. Düzeltir, tekrar "/gonder"
5. Antigravity: ✅ TEST BAŞARILI!
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

**Eğer Emine, Talha veya Baha isen:** Aşağıdaki adımları sırasıyla yap.

---

# ADIM 1: GitHub Davetini Kabul Et ✉️

1. **E-postanı aç** (GitHub'a kayıtlı olan)
2. **"You've been invited..."** başlıklı maili bul
3. **Yeşil butona tıkla:** "Accept invitation"
4. **Giriş yap** (GitHub hesabınla)

## ✅ Kontrol:
- https://github.com/cagriaksoy191-oss/structural_health adresine git
- Sayfayı görebiliyorsan → TAMAM! ✅

---

# ADIM 2: Projeyi Bilgisayarına İndir 📥

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
```powershell
cd C:\Projects
git clone https://github.com/cagriaksoy191-oss/structural_health.git
cd structural_health
```

## ✅ Kontrol:
`dir` yazınca `main.py` gibi dosyaları görüyorsan → TAMAM! ✅

---

# ADIM 3: Python Kur 🐍

### 3.1 Python Var mı Kontrol Et
```powershell
py --version
```
- "Python 3.11.x" yazıyorsa → ADIM 3.2'yi ATLA
- Hata veriyorsa → ADIM 3.2'yi yap

### 3.2 Python İndir ve Kur
1. https://www.python.org/downloads/ adresine git
2. "Download Python 3.11.x" butonuna tıkla
3. ⚠️ **ÖNEMLİ:** "Add Python to PATH" kutusunu İŞARETLE!
4. "Install Now" tıkla
5. Bilgisayarı YENIDEN BAŞLAT

### 3.3 Sanal Ortam Oluştur
```powershell
cd C:\Projects\structural_health
py -3.11 -m venv venv
.\venv\Scripts\Activate
pip install -r requirements.txt
```

---

# ADIM 4: Ollama Kur (Yapay Zeka İçin) 🤖

1. https://ollama.ai adresine git
2. "Download" butonuna tıkla ve kur
3. YENİ bir PowerShell aç ve yaz:
```powershell
ollama pull qwen3:8b
```
⚠️ Bu 5-10 GB indirecek! 10-30 dakika sürebilir.

## ✅ Kontrol:
```powershell
ollama list
```
"qwen3:8b" görünüyorsan → TAMAM! ✅

---

# ADIM 5: Model Dosyalarını Al 📁

Bazı dosyalar çok büyük olduğu için GitHub'da yok. Çağrı'dan al:
- `concrete_model.joblib`
- `risk_model.joblib`
- `anfis_model_agirliklari.pth`

Bu dosyaları `C:\Projects\structural_health` klasörüne koy.

---

# ADIM 6: Self-Hosted Runner Kur 🏃

## Bu Ne?
GitHub'dan test komutlarını alan program. Push yaptığında kendi bilgisayarında test çalışır.

### 6.1 GitHub'dan Token Al
https://github.com/cagriaksoy191-oss/structural_health/settings/actions/runners/new adresine git.

### 6.2 Runner Klasörü Oluştur
```powershell
mkdir C:\actions-runner
cd C:\actions-runner
```

### 6.3 Runner'ı İndir
GitHub sayfasındaki "Download" komutunu kopyala-yapıştır.

### 6.4 Yapılandır
GitHub sayfasındaki "Configure" komutunu çalıştır.

Sana birkaç soru soracak:
- **Runner name:** Kendi adını yaz!
  - Emine → `emine-pc`
  - Talha → `talha-pc`
  - Baha → `baha-pc`

---

# ADIM 7: Antigravity Kur 🚀

## Bu Adım Çok Önemli!

Antigravity, bizim kurduğumuz otomasyonları çalıştıran IDE.

### 7.1 Antigravity'yi İndir
1. https://antigravity.dev adresine git
2. Windows sürümünü indir
3. Kur ve aç

### 7.2 Brave Tarayıcısını Ayarla
1. Antigravity'de `Ctrl + ,` bas (Ayarlar açılır)
2. Arama çubuğuna "browser" yaz
3. **"Chrome Binary Path"** alanına şunu yaz:
```
C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe
```

> 💡 Bu sayede Antigravity, GitHub Actions sayfasını otomatik kontrol edebilecek.

---

# ADIM 8: Her Şeyi Test Et ✅

Antigravity'yi aç ve şu komutu yaz:

```
/test
```

"TÜM KRİTİK KONTROLLER BAŞARILI" görüyorsan → HER ŞEY TAMAM! 🎉

---

# 📅 GÜNLÜK KULLANIM

## Artık Çok Basit!

### 🚀 SİHİRLİ KOMUT (TEK KOMUTLA HER ŞEY!)

Akşam bilgisayarı kapatmadan önce şunu yaz:

> **"Runner'ı kontrol et, arkadaşlarımın değişikliklerini çek, çakışma varsa her iki tarafın en iyi kısımlarını birleştir ve neden bu kararı verdiğini açıkla, sonra benim değişikliklerimi GitHub'a gönder, CI/CD testini bekle ve projeyi tarayıcıda test edip sonucu göster"**

Bu tek komut otomatik olarak:
- ✅ Arkadaşların değişikliklerini çeker
- ✅ Çakışma varsa akıllıca çözer
- ✅ Senin değişikliklerini gönderir
- ✅ Test eder ve sonucu gösterir

### Alternatif: Tek Tek Komutlar

☀️ Sabah (Bilgisayarı açınca):
```
/sabah
```

💻 Gün içi:
Kodunu yaz, istediğin kadar çalış.

📤 İşin bitince:
```
/gonder
```

✅ Sonucu görmek için:
```
/kontrol
```

---

# ⚡ TÜM KOMUTLAR

| Komut | Ne Yapar | Ne Zaman Kullan |
|-------|----------|-----------------|
| `/sabah` | Git pull + venv aktif | Günün başında |
| `/gonder` | Git add/commit/push | Kod bitince |
| `/kontrol` | GitHub Actions durumu | Push'tan sonra |
| `/test` | Health check | Test etmek için |
| `/runner` | Runner başlat | PC açıldığında |

---

# ❓ SIKÇA KARŞILAŞILAN SORUNLAR

| Hata | Çözüm |
|------|-------|
| `/sabah` çalışmıyor | Antigravity'yi kapat, tekrar aç |
| "Model bulunamadı" | .joblib dosyaları eksik, Çağrı'dan al |
| "Ollama bağlantı hatası" | Başlat menüsünden "Ollama" aç |
| "Runner offline" | `/runner` yaz |
| Tarayıcı açılmıyor | Brave ayarlarını kontrol et |

---

# 📊 KURULUM KONTROL LİSTESİ

| Adım | Ne Yaptın? | Kontrol |
|------|------------|---------|
| 1 | GitHub daveti | Repo sayfası açılıyor mu? |
| 2 | Projeyi klonla | `dir` ile dosyalar görünüyor mu? |
| 3 | Python kur | `py --version` çalışıyor mu? |
| 4 | Ollama kur | `ollama list` çalışıyor mu? |
| 5 | Model dosyaları | .joblib dosyaları var mı? |
| 6 | Runner kur | GitHub'da "Idle" görünüyor mu? |
| 7 | Antigravity kur | `/test` çalışıyor mu? |

**7'si de ✅ ise: SEN HAZIRSIN!** 🎉

---

# 📱 YARDIM LAZIMSA

1. 📖 Bu rehberi tekrar oku
2. 🤖 Antigravity'ye "yardım et" de
3. 💬 Grup sohbetine yaz
4. 📞 Çağrı'yı ara

---

*Son Güncelleme: 7 Şubat 2026*
*Hazırlayan: Çağrı*
*Takım: Çağrı, Emine, Talha, Baha*
