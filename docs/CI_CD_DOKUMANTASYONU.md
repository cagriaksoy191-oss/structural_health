# V12 Titanium - CI/CD Sistem Dokümantasyonu
## GitHub Actions ile Otomatik Test Sistemi

---

## 📋 İçindekiler
1. [CI/CD Nedir?](#cicd-nedir)
2. [Nasıl Çalışır?](#nasıl-çalışır)
3. [Self-Hosted Runner](#self-hosted-runner)
4. [Sıkça Sorulan Sorular](#sıkça-sorulan-sorular)
5. [Komutlar ve Kullanım](#komutlar-ve-kullanım)

---

## 🤔 CI/CD Nedir?

**CI/CD** = Continuous Integration / Continuous Deployment (Sürekli Entegrasyon / Sürekli Dağıtım)

Bu sistem:
- ✅ Kod değişikliklerini **otomatik olarak test** eder
- ✅ Hataları erken aşamada **tespit** eder
- ✅ Kodun her zaman çalışır durumda olduğunu **garanti** eder

### ⚠️ Önemli Not
CI/CD sistemi **sürekli çalışmaz!** Sadece:
- GitHub'a kod push ettiğinde
- Pull request açtığında
- Manuel tetikleme yaptığında

**Hiçbir değişiklik yoksa = Hiçbir şey çalışmaz!**

---

## ⚙️ Nasıl Çalışır?

```
┌─────────────────────────────────────────────────────────────┐
│                      WORKFLOW AKIŞI                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   1. Kod Yazarsın                                            │
│         ↓                                                    │
│   2. GitHub'a Push Edersin                                   │
│         ↓                                                    │
│   3. GitHub Actions Tetiklenir                               │
│         ↓                                                    │
│   4. Self-Hosted Runner (Bilgisayarın) İşi Alır             │
│         ↓                                                    │
│   5. Testler Çalışır (30-60 saniye)                         │
│         ↓                                                    │
│   6. Sonuç:                                                  │
│      ✅ Başarılı = Her şey yolunda                          │
│      ❌ Başarısız = Bir hata var, düzelt                    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Pipeline Adımları (main.yml)

| Adım | Açıklama | Süre |
|------|----------|------|
| 1. Checkout | Kodu GitHub'dan çeker | ~5 sn |
| 2. Setup Python | Python 3.11 ortamını hazırlar | ~10 sn |
| 3. Upgrade pip | pip paket yöneticisini günceller | ~5 sn |
| 4. Install Dependencies | requirements.txt'i yükler | ~20 sn |
| 5. Health Check | GPU, kütüphane ve Ollama testleri | ~10 sn |
| 6. Verify Main | main.py modülünü doğrular | ~5 sn |
| 7. Complete | Başarı mesajı | ~1 sn |

**Toplam: ~1 dakika**

---

## 🖥️ Self-Hosted Runner

### Nedir?
Self-hosted runner, **senin bilgisayarında** çalışan bir GitHub Actions istemcisidir. GitHub'ın sunucuları yerine kendi RTX GPU'lu bilgisayarını kullanır.

### Neden Gerekli?
- 🎮 **GPU Kullanımı:** GitHub'ın ücretsiz sunucularında GPU yok
- 💾 **Büyük Modeller:** Ollama ve AI modelleri senin bilgisayarında
- ⚡ **Hız:** Yerel ağda daha hızlı çalışır

### Kaynak Kullanımı

| Durum | CPU | RAM | Açıklama |
|-------|-----|-----|----------|
| **Boşta** | %0 | ~15 MB | Yeni iş bekliyor |
| **Test Çalışırken** | %10-30 | ~500 MB | 30-60 saniye sürer |
| **Kapalı** | %0 | 0 MB | Testler beklemede kalır |

### Başlatma ve Durdurma

```powershell
# Runner'ı Başlat (Ayrı pencerede)
C:\actions-runner\run.cmd

# veya PowerShell'den
Start-Process -FilePath "C:\actions-runner\run.cmd" -WorkingDirectory "C:\actions-runner"
```

**Durdurmak için:** Runner penceresinde `Ctrl+C` bas veya pencereyi kapat.

---

## ❓ Sıkça Sorulan Sorular

### S: Runner her zaman açık mı kalmalı?
**C:** Hayır! İstediğin zaman kapatabilirsin.
- Açıksa: Push yaptığında testler hemen çalışır
- Kapalıysa: Testler "beklemede" kalır, runner açınca çalışır

### S: Bilgisayarımı yavaşlatır mı?
**C:** Neredeyse hiç!
- Boştayken: Neredeyse sıfır kaynak kullanır
- Test sırasında: 30-60 saniye hafif yük, sonra biter

### S: Hataları otomatik düzeltir mi?
**C:** Hayır! Sadece **uyarır**. Düzeltme senin işin.
- ✅ geçerse: Kod çalışıyor demek
- ❌ geçmezse: Bir sorun var, logları incele

### S: İnternet olmadan çalışır mı?
**C:** Hayır. GitHub'a bağlanması gerekir.

### S: Runner'ı kapatırsam projeme bir şey olur mu?
**C:** Hayır! Proje dosyaların güvende. Sadece otomatik testler çalışmaz.

---

## 🛠️ Komutlar ve Kullanım

### Git Komutları

```powershell
# Değişiklikleri göster
git status

# Dosyaları ekle
git add .

# Commit yap
git commit -m "Açıklama mesajı"

# GitHub'a gönder (CI/CD tetiklenir!)
git push origin main

# Son commitleri göster
git log --oneline -5
```

### Runner Komutları

```powershell
# Runner'ı başlat
C:\actions-runner\run.cmd

# Runner durumunu kontrol et (loglar)
Get-Content "C:\actions-runner\_diag\Runner_*.log" -Tail 20

# Çalışan processler
Get-Process | Where-Object { $_.ProcessName -like "*Runner*" }
```

### Test Komutları

```powershell
# Health check testini manuel çalıştır
py -3.11 tests/health_check.py

# Backend sunucuyu başlat
py -3.11 main.py

# API'yi test et
Invoke-RestMethod -Uri http://127.0.0.1:8000/
```

---

## 📁 Proje Yapısı

```
V12_Titanium/
├── .github/
│   └── workflows/
│       └── main.yml          # CI/CD workflow tanımı
├── tests/
│   └── health_check.py       # Otomatik test scripti
├── docs/
│   └── CI_CD_DOKUMANTASYONU.md  # Bu dosya
├── main.py                   # FastAPI backend
├── index.html                # Web arayüzü
├── requirements.txt          # Python bağımlılıkları
├── .gitignore               # Git'ten hariç tutulanlar
└── [model dosyaları]         # .gitignore'da, GitHub'a yüklenmez
```

---

## 🔗 Faydalı Linkler

- **GitHub Actions Sayfası:** `https://github.com/[kullanıcı]/structural_health/actions`
- **Workflow Dosyası:** `.github/workflows/main.yml`
- **Test Scripti:** `tests/health_check.py`

---

## 📝 Notlar

1. **Model Dosyaları:** `.joblib`, `.pth`, `.pkl` dosyaları `.gitignore`'da. GitHub'a yüklenmezler. Runner'da manuel olarak bulunmalılar.

2. **Secrets (Gizli Anahtarlar):** API anahtarları GitHub Secrets'ta saklanmalı:
   - Repository → Settings → Secrets → Actions → New repository secret

3. **Workflow Tetikleme:** `workflow_dispatch` aktif, GitHub'dan manuel tetikleme yapılabilir:
   - Actions → V12 Titanium CI/CD → Run workflow

---

*Son Güncelleme: 4 Şubat 2026*
*V12 Titanium - Yapısal Sağlık İzleme Sistemi*
