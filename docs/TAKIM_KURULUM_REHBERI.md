# V12 Titanium - Takım Arkadaşları İçin Kurulum Rehberi
## Private Repo Erişimi ve Kendi Bilgisayarında Çalıştırma

---

## 📋 Genel Bakış

Bu rehber, **private GitHub reposuna** erişim sağlayıp, **kendi bilgisayarınızda** projeyi çalıştırmanızı sağlar.

**Önemli:** Her takım üyesi:
- ✅ Kendi bilgisayarında çalışır (başkasının kaynağını kullanmaz)
- ✅ Kendi Self-Hosted Runner'ını kurar
- ✅ Kendi Ollama (LLM) kurulumunu yapar
- ✅ GitHub'a push yaptığında kendi bilgisayarında test çalışır

---

## 🔐 ADIM 1: GitHub Repo Erişimi (Repo Sahibi Yapacak)

### Repo sahibi (Çağrı) şunları yapmalı:

1. **GitHub'da repoya git:**
   ```
   https://github.com/cagriaksoy191-oss/structural_health
   ```

2. **Settings → Collaborators → Add people**

3. **Arkadaşlarının GitHub kullanıcı adlarını ekle:**
   - Her arkadaş için "Add collaborator" tıkla
   - Kullanıcı adını yaz ve davet gönder

4. **Arkadaşlar e-postalarına gelen daveti kabul etmeli**

---

## 💻 ADIM 2: Projeyi Klonlama (Her Arkadaş Yapacak)

```powershell
# 1. İstediğin klasöre git
cd C:\Projects

# 2. Repoyu klonla
git clone https://github.com/cagriaksoy191-oss/structural_health.git

# 3. Proje klasörüne gir
cd structural_health
```

---

## 🐍 ADIM 3: Python Ortamı Kurulumu

```powershell
# 1. Python 3.11 yüklü olmalı (python.org'dan indir)

# 2. Virtual environment oluştur
py -3.11 -m venv venv

# 3. Aktif et
.\venv\Scripts\Activate

# 4. Bağımlılıkları yükle
pip install -r requirements.txt
```

---

## 🤖 ADIM 4: Ollama (LLM) Kurulumu

### 4.1 Ollama İndir ve Kur
1. https://ollama.ai adresine git
2. Windows sürümünü indir ve kur
3. Kurulum tamamlandığında otomatik başlar

### 4.2 Qwen Modelini İndir
```powershell
# Terminalde çalıştır (5-10 GB indirecek!)
ollama pull qwen3:8b
```

### 4.3 Test Et
```powershell
# Ollama çalışıyor mu?
ollama list
# Qwen3:8b görünmeli
```

---

## 🏃 ADIM 5: Self-Hosted Runner Kurulumu

> ⚠️ **ÖNEMLİ:** Her arkadaş KENDİ runner'ını kurmalı. Bu sayede push yaptığında kendi bilgisayarında test çalışır.

### 5.1 GitHub'dan Runner İndir

1. **Repo sayfasına git:** `https://github.com/cagriaksoy191-oss/structural_health`

2. **Settings → Actions → Runners → New self-hosted runner**

3. **Windows seçeneğini tıkla**

4. **Komutları sırayla çalıştır:**

```powershell
# 1. Klasör oluştur
mkdir C:\actions-runner
cd C:\actions-runner

# 2. Runner'ı indir (GitHub'daki güncel linki kullan!)
Invoke-WebRequest -Uri https://github.com/actions/runner/releases/download/v2.XXX.X/actions-runner-win-x64-2.XXX.X.zip -OutFile actions-runner.zip

# 3. Çıkart
Expand-Archive -Path actions-runner.zip -DestinationPath .

# 4. Yapılandır (GitHub'dan aldığın token'ı kullan!)
.\config.cmd --url https://github.com/cagriaksoy191-oss/structural_health --token XXXXXXXXXXXXX

# 5. Runner'ı başlat
.\run.cmd
```

### 5.2 Runner'ı Etiketle (Önemli!)

Yapılandırma sırasında runner'a **benzersiz bir isim** ver:
- Emine: `emine-pc`
- Talha: `talha-pc`
- Baha: `baha-pc`

Bu sayede kimin runner'ı çalıştığı belli olur.

---

## 🔧 ADIM 6: Model Dosyalarını Kopyala

`.gitignore` nedeniyle büyük model dosyaları GitHub'da yok. Bu dosyaları **USB veya bulut** ile paylaşın:

```
concrete_model.joblib      (~4 MB)
risk_model.joblib          (~8 MB)
anfis_model_agirliklari.pth (~3 KB)
```

Bu dosyaları proje ana klasörüne kopyalayın.

---

## ✅ ADIM 7: Test Et

### 7.1 Backend Sunucu
```powershell
py -3.11 main.py
# "Uvicorn running on http://127.0.0.1:8000" görmeli
```

### 7.2 Health Check
```powershell
py -3.11 tests/health_check.py
# "TÜM KRİTİK KONTROLLER BAŞARILI" görmeli
```

### 7.3 Web Arayüzü
- Tarayıcıda `index.html` dosyasını aç
- Formu doldur ve test et

---

## 🔄 Günlük Çalışma Akışı

```powershell
# 1. En son değişiklikleri çek
git pull origin main

# 2. Kendi değişikliklerini yap
# ... kod yaz ...

# 3. Değişiklikleri kaydet
git add .
git commit -m "Açıklama"

# 4. GitHub'a gönder (CI/CD tetiklenir!)
git push origin main
```

---

## ⚡ Çoklu Runner Senaryosu

### Nasıl Çalışır?

| Kişi | Push Yapar | Kimin Runner'ı Çalışır? |
|------|------------|-------------------------|
| Çağrı | ✅ | Çağrı'nın PC'si (eğer açıksa) |
| Emine | ✅ | Emine'nin PC'si (eğer açıksa) |
| Talha | ✅ | Talha'nın PC'si (eğer açıksa) |
| Baha | ✅ | **İlk müsait olan runner!** |

### Önemli Notlar:
- Tüm runner'lar aynı repoya bağlı
- Push yapıldığında **açık olan ilk runner** işi alır
- Kendi push'un için kendi runner'ının açık olması önerilir
- Başka birinin runner'ı kapalıysa, açık olan başka biri işi alabilir

---

## ❓ Sorun Giderme

### "Permission denied" hatası
→ GitHub davetini kabul etmediniz. E-postanızı kontrol edin.

### "Model bulunamadı" hatası
→ `.joblib` ve `.pth` dosyaları eksik. USB ile kopyalayın.

### "Ollama bağlantı hatası"
→ Ollama çalışmıyor. `ollama serve` komutunu çalıştırın.

### "Runner offline" görünüyor
→ `C:\actions-runner\run.cmd` çalıştırın.

---

## 📞 İletişim

Sorun yaşarsanız takım grubunda paylaşın!

*Son Güncelleme: 4 Şubat 2026*
