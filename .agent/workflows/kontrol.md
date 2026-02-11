---
description: GitHub Actions durumunu tarayıcıda kontrol et
---

# /kontrol - GitHub Actions Kontrolü Workflow

Bu workflow, GitHub Actions durumunu kontrol eder. Tarayıcı veya komut satırı ile çalışır.

## Adımlar

### 1. GitHub Actions sayfasını kontrol et

**Yöntem A — Tarayıcı aracın varsa (browser tool):**
Tarayıcıda şu URL'yi aç:
```
https://github.com/cagriaksoy191-oss/structural_health/actions
```

### 2. Son workflow run'ı kontrol et
Sayfadaki ilk workflow run'ın durumunu oku:
- ✅ Yeşil tik = Başarılı
- ❌ Kırmızı X = Hata var
- 🟡 Sarı daire = Çalışıyor

### 3. Sonucu raporla
Kullanıcıya bildir:
- Workflow adı
- Çalışma süresi
- Başarılı mı?

### 4. Hata varsa
Eğer kırmızı X görünüyorsa:
- Workflow'a tıkla
- Hata loglarını oku
- Hatayı kullanıcıya açıkla

## Beklenen Sonuç
```
📊 GitHub Actions Durumu:
━━━━━━━━━━━━━━━━━━━━━
✅ V12 Titanium CI/CD
   Süre: 45 saniye
   Durum: BAŞARILI
   Son commit: "Login sayfası düzeltildi"
━━━━━━━━━━━━━━━━━━━━━
```

## Hata Durumu Örneği
```
❌ V12 Titanium CI/CD - HATA!
━━━━━━━━━━━━━━━━━━━━━
Hata: "ModuleNotFoundError: No module named 'pandas'"
Çözüm: pip install pandas çalıştır
━━━━━━━━━━━━━━━━━━━━━
```

### 5. Yöntem B — Tarayıcı aracın yoksa (komut satırı alternatifi)
```powershell
try {
    $response = Invoke-RestMethod -Uri "https://api.github.com/repos/cagriaksoy191-oss/structural_health/actions/runs?per_page=1" -Method Get -TimeoutSec 10 -ErrorAction Stop
    $run = $response.workflow_runs[0]
    $durum = $run.conclusion
    $baslik = $run.display_title
    if ($durum -eq "success") {
        Write-Host "✅ CI/CD Başarılı: $baslik"
    } elseif ($durum -eq $null) {
        Write-Host "🟡 CI/CD Çalışıyor: $baslik"
    } else {
        Write-Host "❌ CI/CD Hata: $baslik (Durum: $durum)"
    }
} catch {
    Write-Host "⚠️ GitHub API'ye erişilemedi. Manuel kontrol gerekebilir."
    Write-Host "   URL: https://github.com/cagriaksoy191-oss/structural_health/actions"
}
```
