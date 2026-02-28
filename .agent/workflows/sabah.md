---
description: Günü başlat - Git pull ve venv aktivasyonu
---

# /sabah - Günü Başlat Workflow

Bu workflow, her sabah çalışmaya başlamadan önce projeyi güncel hale getirir.
4 kişilik ekipte herkesin bilgisayarında sorunsuz çalışır.

> **NOT:** Bu workflow proje klasörü içinden çalıştırılmalıdır. Agent zaten doğru klasördedir.
> **OPTİMİZASYON:** Hash-tabanlı cache ile bağımlılık kontrolü. Değişiklik yoksa pip/npm install atlanır (~40dk → ~5sn).

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

### 2. Akıllı bağımlılık kontrolü (hash-tabanlı cache)

```powershell
# --- Cache dosyası yolu ---
$cacheFile = ".sabah_cache"

# --- Yardımcı: Dosya hash hesapla ---
function Get-FileHashValue($filePath) {
    if (Test-Path $filePath) {
        return (Get-FileHash -Path $filePath -Algorithm SHA256).Hash
    }
    return $null
}

# --- Yardımcı: Cache oku ---
function Read-SabahCache {
    if (Test-Path $cacheFile) {
        try {
            return (Get-Content $cacheFile -Raw | ConvertFrom-Json)
        } catch {
            return $null
        }
    }
    return $null
}

# --- Yardımcı: Cache yaz ---
function Write-SabahCache($reqHash, $pkgHash) {
    $cache = @{
        requirements_hash = $reqHash
        package_json_hash = $pkgHash
        last_updated      = (Get-Date -Format "yyyy-MM-ddTHH:mm:ss")
    }
    $cache | ConvertTo-Json | Set-Content $cacheFile -Encoding UTF8
}

# --- Mevcut cache'i oku ---
$cache = Read-SabahCache
$currentReqHash = Get-FileHashValue "requirements.txt"
$currentPkgHash = Get-FileHashValue "frontend\package.json"
$cachedReqHash  = if ($cache) { $cache.requirements_hash } else { $null }
$cachedPkgHash  = if ($cache) { $cache.package_json_hash } else { $null }

# =============================================
# PYTHON BAĞIMLILIKLARI
# =============================================
if (Test-Path "venv\Scripts\python.exe") {
    Write-Host "✅ Python venv mevcut"
    & venv\Scripts\python -c "import fastapi; import torch; print('✅ Kritik kutuphaneler yuklu')" 2>&1

    if ($currentReqHash -eq $cachedReqHash) {
        $shortHash = $currentReqHash.Substring(0, 12)
        Write-Host "✅ requirements.txt degismemis (hash: $shortHash), pip install atlaniyor"
    } else {
        Write-Host "📦 requirements.txt degismis, bagimliliklar guncelleniyor..."
        & venv\Scripts\pip install -r requirements.txt --progress-bar off 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Python bagimliliklari guncellendi"
        } else {
            Write-Host "❌ pip install basarisiz! (exit code: $LASTEXITCODE)"
            Write-Host "⚠️ Cache guncellenmedi, sonraki calistirmada tekrar denenecek"
            $currentReqHash = $cachedReqHash  # hash'i eski tut, tekrar dene
        }
    }
} else {
    Write-Host "⚠️ venv bulunamadi. Olusturuluyor..."
    python -m venv venv
    & venv\Scripts\pip install -r requirements.txt --progress-bar off 2>&1
    Write-Host "✅ venv olusturuldu ve bagimliliklar yuklendi"
}

# =============================================
# FRONTEND BAĞIMLILIKLARI
# =============================================
if (Test-Path "frontend\package.json") {
    Push-Location frontend
    if (-not (Test-Path "node_modules")) {
        Write-Host "📦 Frontend node_modules kuruluyor (ilk kurulum)..."
        npm install --loglevel warn 2>&1
        Write-Host "✅ Frontend bagimliliklari kuruldu"
    } elseif ($currentPkgHash -ne $cachedPkgHash) {
        Write-Host "📦 package.json degismis, npm install calistiriliyor..."
        npm install --loglevel warn 2>&1
        Write-Host "✅ Frontend bagimliliklari guncellendi"
    } else {
        Write-Host "✅ Frontend bagimliliklari guncel (package.json degismemis)"
    }
    Pop-Location
}

# --- Cache'i güncelle ---
Write-SabahCache $currentReqHash $currentPkgHash
Write-Host "💾 Cache guncellendi: .sabah_cache"
```

### 3. Durumu Raporla

Kullanıcıya şunları bildir:

- Git pull sonucu (yeni dosya var mı?)
- Venv ve kütüphaneler hazır mı?
- Bağımlılık kurulumu atlandı mı yoksa çalıştırıldı mı?
- Çalışmaya hazır mısın?

## Beklenen Sonuç

```
✅ Git pull tamamlandı (güncel)
✅ Python venv ve kütüphaneler mevcut
✅ requirements.txt değişmemiş (hash: a1b2c3d4...), pip install atlanıyor
✅ Frontend bağımlılıkları güncel (package.json değişmemiş)
💾 Cache güncellendi: .sabah_cache
✅ Çalışmaya hazırsın!
```
