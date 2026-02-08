---
description: GitHub Actions Self-Hosted Runner'ı başlat
---

# /runner - Runner Başlat Workflow

Bu workflow, GitHub Actions self-hosted runner'ı başlatır.

## Adımlar

### 1. Runner klasörüne git
// turbo
```powershell
cd C:\actions-runner
```

### 2. Runner'ı başlat
```powershell
.\run.cmd
```

### 3. Bağlantıyı bekle
Şu mesajı gör:
```
√ Connected to GitHub
Listening for Jobs
```

### 4. Durumu raporla
Kullanıcıya bildir:
- Runner başarıyla bağlandı mı?
- Pencereyi kapatmaması gerektiğini hatırlat

## Beklenen Sonuç
```
🏃 Runner Durumu:
━━━━━━━━━━━━━━━━━━━━━
✅ GitHub'a bağlandı
✅ İş dinleniyor (Listening for Jobs)
━━━━━━━━━━━━━━━━━━━━━

⚠️ ÖNEMLİ: Bu pencereyi KAPATMA!
   Küçült ve öyle bırak.
```

## Hata Durumları
| Hata | Çözüm |
|------|-------|
| "Runner already running" | Zaten çalışıyor, bir şey yapma |
| "Cannot connect" | İnternet bağlantını kontrol et |
| "Config.cmd not found" | Runner kurulmamış, TAKIM_KURULUM_REHBERI'ne bak |

## Notlar
- Runner sadece bilgisayar açıkken çalışır
- Bilgisayarı her açtığında bu komutu çalıştır
- Çalışırken pencereyi küçült, KAPATMA
