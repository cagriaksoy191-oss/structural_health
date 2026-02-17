---
description: Günü başlat - Git pull ve venv aktivasyonu
---

# /sabah - Günü Başlat Workflow

Bu workflow, her sabah çalışmaya başlamadan önce projeyi güncel hale getirir.
4 kişilik ekipte herkesin bilgisayarında sorunsuz çalışır.

> **NOT:** Bu workflow proje klasörü içinden çalıştırılmalıdır. Agent zaten doğru klasördedir.

// turbo-all

## Adımlar

### 1. Son değişiklikleri çek
```powershell
$pullOutput = cmd /c "git pull origin main" 2>&1
Write-Host $pullOutput
```
**🤖 AGENT TALİMATI:** Eğer çıktıda "CONFLICT" kelimesi varsa:
1. `git diff --name-only --diff-filter=U` ile çakışan dosyaları bul
2. Her dosyada `<<<<<<<` ve `>>>>>>>` işaretlerini bul, iki değişikliği birleştir
3. **RAPORLAMA YAP (ÖNEMLİ):** Çakışmayı çözdükten sonra kullanıcıya şu formatta bir özet sun:
    - **Çakışan Dosya:** [Dosya Adı]
    - **Gelen Değişiklik:** [Arkadaşın ne yapmış?]
    - **Senin Değişikliğin:** [Sen ne yapmıştın?]
    - **Çözüm:** [Nasıl birleştirdin?]
4. `git add .; git commit -m "Merge conflict cozuldu (AI-assisted)"` çalıştır
5. Hiç conflict yoksa bu adımı atla.

### 2. Bağımlılıkları kontrol et ve güncelle
```powershell
# Python venv kontrolü
if (Test-Path "venv\Scripts\python.exe") {
    Write-Host "✅ Python venv mevcut"
    & venv\Scripts\python -c "import fastapi; import torch; print('✅ Kritik kütüphaneler yüklü')" 2>&1
    # Arkadaş yeni paket eklemiş olabilir — pip senkronize et
    & venv\Scripts\pip install -r requirements.txt --quiet 2>&1 | Out-Null
    Write-Host "✅ Python bağımlılıkları güncel"
} else {
    Write-Host "⚠️ venv bulunamadı. Oluşturuluyor..."
    python -m venv venv
    & venv\Scripts\pip install -r requirements.txt
    Write-Host "✅ venv oluşturuldu ve bağımlılıklar yüklendi"
}

# Frontend bağımlılıkları (package.json değişmiş olabilir)
if (Test-Path "frontend\package.json") {
    Push-Location frontend
    if (-not (Test-Path "node_modules")) {
        Write-Host "📦 Frontend node_modules kuruluyor..."
        npm install --silent 2>&1 | Out-Null
        Write-Host "✅ Frontend bağımlılıkları kuruldu"
    } else {
        Write-Host "✅ Frontend node_modules mevcut"
    }
    Pop-Location
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
✅ Frontend bağımlılıkları güncel
✅ Çalışmaya hazırsın!
```
