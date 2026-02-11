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
git push origin main
```

### 6. Sonucu raporla
- Push başarılı mı?
- GitHub Actions workflow tetiklendi mi?

**🤖 AGENT TALİMATI:** Push reddedilirse:
1. `git pull --rebase origin main` çalıştır, conflict varsa çöz
2. Tekrar `git push origin main` dene

## Beklenen Sonuç
```
✅ X dosya değişti
✅ Commit: "kullanıcının mesajı"
✅ GitHub'a gönderildi
⏳ GitHub Actions çalışıyor...
```
