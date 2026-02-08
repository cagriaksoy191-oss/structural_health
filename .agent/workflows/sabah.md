---
description: Günü başlat - Git pull ve venv aktivasyonu
---

# /sabah - Günü Başlat Workflow

Bu workflow, her sabah çalışmaya başlamadan önce yapılması gereken adımları otomatize eder.

## Adımlar

### 1. Proje klasörüne git
// turbo
```powershell
cd C:\Projects\structural_health
```

### 2. Son değişiklikleri çek
```powershell
git pull origin main
```

### 3. Sanal ortamı aktif et
// turbo
```powershell
.\venv\Scripts\Activate
```

### 4. Durumu Raporla
Kullanıcıya şunları bildir:
- Git pull sonucu (yeni dosya var mı?)
- Venv aktif mi?
- Çalışmaya hazır mısın?

## Beklenen Sonuç
```
✅ Git pull tamamlandı
✅ Sanal ortam aktif (venv)
✅ Çalışmaya hazırsın!
```
