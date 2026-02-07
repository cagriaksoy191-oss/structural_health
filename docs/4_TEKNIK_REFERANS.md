# ⚙️ V12 Titanium - Teknik Referans Dokümanı

Bu doküman, CI/CD sisteminin (Sürekli Entegrasyon / Dağıtım) nasıl çalıştığını, GitHub Actions yapılandırmasını ve Self-Hosted Runner detaylarını açıklar.
Genellikle **teknik ekip** ve **sistem yöneticileri** içindir.

---

## 🏗️ SİSTEM MİMARİSİ

Projemiz hibrit bir CI/CD yapısı kullanır:

1. **GitHub Actions (Bulut):** Workflow yönetimini sağlar.
2. **Self-Hosted Runner (Lokal):** Testleri **Çağrı'nın bilgisayarında** (RTX GPU ile) çalıştırır.
3. **Antigravity (IDE):** Geliştiricilerin komutları kolayca tetiklemesini sağlar.

### Neden Self-Hosted Runner?
- 🎮 **GPU Erişimi:** Yapay zeka modelleri (Qwen3, PyTorch) GPU gerektirir.
- 💾 **Büyük Dosyalar:** Model dosyaları (GB'larca) yerel diskte saklanır, her testte indirilmez.
- ⚡ **Hız:** Yerel ağda çalıştığı için testler çok daha hızlıdır.

---

## 🔄 WORKFLOW AKIŞI (`main.yml`)

Her `push` işleminde (veya manuel tetiklemede) şu adımlar çalışır:

1. **Checkout:** Kod GitHub'dan çekilir.
2. **Setup Python:** Python 3.11 ortamı hazırlanır.
3. **Dependencies:** `requirements.txt` yüklenir.
4. **Health Check:**
   - GPU kontrolü (`torch.cuda.is_available()`)
   - Model dosyaları kontrolü (`.joblib`, `.pth`)
   - Ollama servisi kontrolü
5. **Integration Test:** `main.py` ve temel fonksiyonlar test edilir.

**Tahmini Süre:** 30 - 60 saniye.

---

## 🖥️ SELF-HOSTED RUNNER YÖNETİMİ

Runner, `C:\actions-runner` klasöründe kuruludur.

### Durum Kontrolü
PowerShell'de şu komutu yazın:
```powershell
Get-Service "actions.runner.*"
```
Veya Antigravity'de `/runner` komutunu kullanın.

### Manuel Başlatma
Eğer servis çalışmıyorsa:
```powershell
cd C:\actions-runner
.\run.cmd
```

### Servis Olarak Kurma (Opsiyonel)
Otomatik başlaması için:
```powershell
.\svc.cmd install
.\svc.cmd start
```

---

## 🛠️ SIK KARŞILAŞILAN HATA KODLARI

| Hata Kodu | Anlamı | Çözüm |
|-----------|--------|-------|
| `Process completed with exit code 1` | Genel Python hatası | Logları inceleyin, kütüphane eksik olabilir. |
| `Torch not compiled with CUDA` | GPU bulunamadı | PyTorch sürümünü kontrol edin. |
| `Ollama connection refused` | Ollama kapalı | `ollama serve` veya uygulamasını başlatın. |
| `Runner is offline` | Runner kapalı | Çağrı'nın bilgisayarını kontrol edin. |

---

## 📂 DOSYA YAPISI

```
structural_health/
├── .github/workflows/main.yml  # CI/CD Workflow
├── .agent/workflows/*.md       # Antigravity Komutları
├── docs/                       # Dokümantasyon (BU KLASÖR)
├── tests/health_check.py       # Test Scripti
├── main.py                     # Ana Uygulama
└── requirements.txt            # Bağımlılıklar
```

---

*Son Güncelleme: 7 Şubat 2026*
