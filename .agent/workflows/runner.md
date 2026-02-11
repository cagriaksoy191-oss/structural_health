---
description: GitHub Actions Self-Hosted Runner'ı başlat
---

# /runner - Runner Başlat Workflow

Bu workflow, GitHub Actions self-hosted runner'ı başlatır.

> **NOT:** Runner sadece runner kurulu bilgisayarlarda çalışır. Kurulu değilse bu adım otomatik atlanır.

## Adımlar

### 1. Runner durumunu kontrol et
// turbo
```powershell
$runnerPath = "C:\actions-runner"
if (Test-Path $runnerPath) {
    $runner = Get-Process "Runner.Listener" -ErrorAction SilentlyContinue
    if ($runner) {
        Write-Host "✅ Runner Zaten Çalışıyor"
    } else {
        Write-Host "⚠️ Runner Kapalı, Başlatılıyor..."
        Start-Process cmd -ArgumentList "/k cd $runnerPath & .\run.cmd"
        Write-Host "✅ Runner Başlatıldı"
    }
} else {
    Write-Host "ℹ️ Bu bilgisayarda GitHub Runner kurulu değil."
    Write-Host "   Runner kurmak için: https://github.com/cagriaksoy191-oss/structural_health/settings/actions/runners"
}
```

### 2. Durumu raporla
Kullanıcıya bildir:
- Runner başarıyla bağlandı mı?
- Pencereyi kapatmaması gerektiğini hatırlat

## Beklenen Sonuç
```
🏃 Runner Durumu:
━━━━━━━━━━━━━━━━━━━━━
✅ Runner çalışıyor
━━━━━━━━━━━━━━━━━━━━━
⚠️ ÖNEMLİ: Runner penceresini KAPATMA! Küçült ve öyle bırak.
```
