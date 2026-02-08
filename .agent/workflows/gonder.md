---
description: Değişiklikleri GitHub'a gönder - git add, commit ve push
---

# /gonder - Değişiklikleri Gönder Workflow

Bu workflow, kod değişikliklerini GitHub'a tek komutla gönderir.

## Adımlar

### 1. Proje klasörüne git
// turbo
```powershell
cd C:\Projects\structural_health
```

### 2. Değişiklikleri göster
```powershell
git status
```
Kullanıcıya değişen dosyaları göster.

### 3. Tüm değişiklikleri ekle
```powershell
git add .
```

### 4. Commit mesajı al
Kullanıcıya sor: "Ne yaptığını kısaca yaz (örn: Login sayfası düzeltildi)"

### 5. Commit yap
```powershell
git commit -m "KULLANICI_MESAJI"
```

### 6. GitHub'a gönder
```powershell
git push origin main
```

### 7. Sonucu raporla
- Push başarılı mı?
- GitHub Actions workflow tetiklendi mi?

## Beklenen Sonuç
```
✅ 3 dosya değişti
✅ Commit: "Login sayfası düzeltildi"
✅ GitHub'a gönderildi
⏳ GitHub Actions çalışıyor...
```

## Hata Durumları
- "Push rejected" → Önce `git pull origin main` yap
- "Nothing to commit" → Değişiklik yok, dosyaları kaydet (CTRL+S)
