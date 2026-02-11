---
description: Günü başlat - Git pull ve venv aktivasyonu
---

# /sabah - Günü Başlat Workflow

Bu workflow, her sabah çalışmaya başlamadan önce projeyi güncel hale getirir.

> **NOT:** Bu workflow proje klasörü içinden çalıştırılmalıdır. Agent zaten doğru klasördedir.

// turbo-all

## Adımlar

### 1. Son değişiklikleri çek
```powershell
git pull origin main
```
**🤖 AGENT TALİMATI:** Eğer conflict çıkarsa, `/gunsonu` workflow'undaki Adım 4'teki çakışma çözme talimatını uygula.

### 2. Bağımlılıkları kontrol et
```powershell
if (Test-Path "venv\Scripts\python.exe") {
    Write-Host "✅ Python venv mevcut"
    & venv\Scripts\python -c "import fastapi; import torch; print('✅ Kritik kütüphaneler yüklü')" 2>&1
} else {
    Write-Host "⚠️ venv bulunamadı. 'python -m venv venv' ile oluştur, sonra 'pip install -r requirements.txt' çalıştır."
}
```

### 3. Durumu Raporla
Kullanıcıya şunları bildir:
- Git pull sonucu (yeni dosya var mı?)
- Venv ve kütüphaneler hazır mı?
- Çalışmaya hazır mısın?

## Beklenen Sonuç
```
✅ Git pull tamamlandı (güncel)
✅ Python venv ve kütüphaneler mevcut
✅ Çalışmaya hazırsın!
```
