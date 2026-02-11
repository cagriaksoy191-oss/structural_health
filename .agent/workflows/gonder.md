---
description: Değişiklikleri GitHub'a gönder - git add, commit ve push
---

# /gonder - Değişiklikleri Gönder Workflow

Bu workflow, kod değişikliklerini GitHub'a tek komutla gönderir.

> **NOT:** Bu workflow proje klasörü içinden çalıştırılmalıdır. Agent zaten doğru klasördedir.

## Adımlar

### 1. Değişiklikleri göster
// turbo
```powershell
git status --short
```
Kullanıcıya değişen dosyaları göster.

### 2. Tüm değişiklikleri ekle
// turbo
```powershell
git add .
```

### 3. Commit mesajı oluştur
Kullanıcıya sor: **"Ne yaptığını kısaca yaz (örn: Login sayfası düzeltildi)"**
Eğer kullanıcı bir mesaj vermezse, değişen dosyalara bakarak otomatik anlamlı bir mesaj oluştur.

### 4. Commit yap
```powershell
git commit -m "KULLANICININ_VERDIGI_MESAJ"
```

### 5. GitHub'a gönder
```powershell
$pushOutput = cmd /c "git push origin main" 2>&1
Write-Host $pushOutput
```

**🤖 AGENT TALİMATI:**
- `git push` komutu PowerShell'de exit code 1 dönebilir — bu bilinen bir PowerShell/stderr sorunudur. Çıktıda **"rejected"** veya **"non-fast-forward"** kelimeleri YOKSA push başarılıdır.
- Push reddedilirse:
  1. `cmd /c "git pull --rebase origin main" 2>&1` çalıştır
  2. Conflict varsa çöz (her iki kodun en iyi kısımlarını birleştir)
  3. Tekrar `cmd /c "git push origin main" 2>&1` dene

### 6. Sonucu raporla
- Push başarılı mı?
- GitHub Actions workflow tetiklendi mi?

## Beklenen Sonuç
```
✅ X dosya değişti
✅ Commit: "kullanıcının mesajı"
✅ GitHub'a gönderildi
⏳ GitHub Actions çalışıyor...
```
