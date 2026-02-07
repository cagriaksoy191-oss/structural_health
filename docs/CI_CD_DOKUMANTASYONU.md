# V12 Titanium - CI/CD Sistem Dokümantasyonu
## GitHub Actions ile Otomatik Test Sistemi

---

## 📋 İçindekiler
1. [CI/CD Nedir?](#cicd-nedir)
2. [Nasıl Çalışır?](#nasıl-çalışır)
3. [Antigravity Komutları](#antigravity-komutları)
4. [Self-Hosted Runner](#self-hosted-runner)
5. [Sıkça Sorulan Sorular](#sıkça-sorulan-sorular)
6. [İleri Düzey: Manuel Komutlar](#ileri-düzey-manuel-komutlar)

---

## 🤔 CI/CD Nedir?

**CI/CD** = Continuous Integration / Continuous Deployment (Sürekli Entegrasyon / Sürekli Dağıtım)

### Gerçek Hayat Örneği

Düşün ki grup ödevi yapıyorsunuz:

### ❌ CI/CD OLMADAN:
```
1. Emine kod yazar, "çalışıyor" der
2. Talha çeker, ÇALIŞMIYOR! 😱
3. 2 saat hata aranır...
4. Sonunda: Bir kütüphane eksikmiş 🤦
```

### ✅ CI/CD İLE:
```
1. Emine kod yazar, "/gonder" der
2. 30 saniye sonra: ❌ HATA VAR!
3. Emine hemen düzeltir, tekrar "/gonder"
4. ✅ BAŞARILI! Artık herkes kullanabilir 🎉
```

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
│   2. /gonder yazarsın (Antigravity'de)                      │
│         ↓                                                    │
│   3. GitHub Actions Tetiklenir                               │
│         ↓                                                    │
│   4. Self-Hosted Runner (Bilgisayarın) İşi Alır             │
│         ↓                                                    │
│   5. Testler Çalışır (30-60 saniye)                         │
│         ↓                                                    │
│   6. /kontrol ile sonucu görürsün:                          │
│      ✅ Başarılı = Her şey yolunda                          │
│      ❌ Başarısız = Hata var, düzelt                        │
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

## 🚀 Antigravity Komutları

Antigravity IDE kullanarak CI/CD işlemlerini kolayca yapabilirsin:

| Komut | Ne Yapar | Ne Zaman Kullan |
|-------|----------|-----------------|
| `/sabah` | Git pull + venv aktif | Günün başında |
| `/gonder` | Git add/commit/push | Kod bitince |
| `/kontrol` | GitHub Actions durumu | Push'tan sonra |
| `/test` | Lokal health check | Test etmek için |
| `/runner` | Runner başlat | PC açıldığında |

### Günlük Rutin (3 Adım)

```
☀️ Sabah:     /sabah    → Hazır ol
💻 Çalış:     (kod yaz)
📤 Bitince:   /gonder   → Gönder
✅ Bekle:     /kontrol  → Sonucu gör
```

### 🚀 YA DA: TEK KOMUTLA HER ŞEY!

Günün sonunda tek bir komutla her şeyi halledebilirsin:

> **"Runner'ı kontrol et, arkadaşlarımın değişikliklerini çek, çakışma varsa her iki tarafın en iyi kısımlarını birleştir ve neden bu kararı verdiğini açıkla, sonra benim değişikliklerimi GitHub'a gönder, CI/CD testini bekle ve projeyi tarayıcıda test edip sonucu göster"**

Bu komut 5 işlemi tek seferde yapar!

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

### Başlatma

**Antigravity ile:**
```
/runner
```

**Manuel (PowerShell ile):**
```powershell
C:\actions-runner\run.cmd
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

### S: Antigravity şart mı?
**C:** Hayır! Antigravity olmadan da PowerShell ile aynı işleri yapabilirsin. Ama Antigravity daha kolay.

---

## 🛠️ İleri Düzey: Manuel Komutlar

Antigravity kullanmak istemezsen, PowerShell ile:

### Git Komutları

```powershell
# Son değişiklikleri çek (/sabah yerine)
cd C:\Projects\structural_health
git pull origin main
.\venv\Scripts\Activate

# Değişiklikleri gönder (/gonder yerine)
git add .
git commit -m "Açıklama mesajı"
git push origin main
```

### Test Komutları

```powershell
# Health check (/test yerine)
py -3.11 tests/health_check.py

# Backend sunucuyu başlat
py -3.11 main.py
```

---

## 📁 Proje Yapısı

```
structural_health/
├── .github/
│   └── workflows/
│       └── main.yml           # CI/CD workflow tanımı
├── .agent/
│   └── workflows/             # Antigravity slash komutları
│       ├── sabah.md
│       ├── gonder.md
│       ├── kontrol.md
│       ├── test.md
│       └── runner.md
├── tests/
│   └── health_check.py        # Otomatik test scripti
├── docs/
│   ├── GUNLUK_KULLANIM_REHBERI.md
│   ├── TAKIM_KURULUM_REHBERI.md
│   └── CI_CD_DOKUMANTASYONU.md  # Bu dosya
├── main.py                    # FastAPI backend
├── index.html                 # Web arayüzü
└── requirements.txt           # Python bağımlılıkları
```

---

## 🔗 Faydalı Linkler

- **GitHub Actions Sayfası:** https://github.com/cagriaksoy191-oss/structural_health/actions
- **Workflow Dosyası:** `.github/workflows/main.yml`
- **Antigravity Komutları:** `.agent/workflows/`

---

## 📝 Notlar

1. **Model Dosyaları:** `.joblib`, `.pth`, `.pkl` dosyaları `.gitignore`'da. GitHub'a yüklenmezler.

2. **Secrets (Gizli Anahtarlar):** API anahtarları GitHub Secrets'ta saklanmalı.

3. **Workflow Tetikleme:** Manuel tetikleme için: Actions → V12 Titanium CI/CD → Run workflow

---

*Son Güncelleme: 7 Şubat 2026*
*V12 Titanium - Yapısal Sağlık İzleme Sistemi*
