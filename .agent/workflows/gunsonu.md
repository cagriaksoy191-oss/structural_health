---
description: Gün Sonu (End of Day) - Full CI/CD Döngüsü
---

# /gunsonu - Tam Otomatik CI/CD Akışı

Bu workflow, gün sonunda yapılması gereken **TÜM** işlemleri tek seferde halleder.
4 kişilik ekipte herkesin bilgisayarında sorunsuz çalışır.

> **ÖNEMLİ AGENT TALİMATI:** Bu workflow tamamen self-contained (bağımsız). Hiçbir harici bilgiye, geçmiş konuşma hafızasına veya MCP sunucusuna ihtiyaç duymaz. Her adımı sırasıyla çalıştır. Bir adım başarısız olursa durma — hata mesajını kaydet ve bir sonraki adıma geç. En sonda özet raporu ver. Bu talimatlar tüm AI modelleri (Claude, GPT, Gemini, vb.) tarafından anlaşılabilecek şekilde yazılmıştır.

// turbo-all

## Adımlar

### 1. Ortam Kontrolü (Runner + Ollama)
```powershell
# --- Runner Kontrolü ---
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
    Write-Host "ℹ️ Bu bilgisayarda GitHub Runner kurulu değil. (Sorun yok, atlanıyor)"
}

# --- Ollama Kontrolü ---
$ollama = Get-Process "ollama app" -ErrorAction SilentlyContinue
if ($ollama) {
    Write-Host "✅ Ollama Servisi Açık"
    try {
        $models = ollama list 2>&1
        if ($models -match "qwen") { Write-Host "✅ Qwen Modeli Yüklü" }
        else { Write-Host "⚠️ Qwen modeli bulunamadı. (AI yorumlama devre dışı, sorun yok)" }
    } catch {
        Write-Host "⚠️ Ollama list komutu çalıştırılamadı."
    }
} else {
    Write-Host "ℹ️ Ollama kapalı veya yüklü değil. (AI yorumlama devre dışı kalabilir, sorun yok)"
}
```

### 2. Güvenlik Kontrolü (.gitignore + venv)
```powershell
# .gitignore'da kritik klasörlerin olduğundan emin ol
$gitignorePath = ".gitignore"
if (Test-Path $gitignorePath) {
    $content = Get-Content $gitignorePath -Raw
    $kritikler = @("venv/", "__pycache__/", "node_modules/", "docs/referanslar/")
    foreach ($item in $kritikler) {
        if ($content -notmatch [regex]::Escape($item)) {
            Write-Host "⚠️ .gitignore'a ekleniyor: $item"
            Add-Content $gitignorePath "`n$item"
        }
    }
    Write-Host "✅ .gitignore güvenlik kontrolü tamamlandı"
} else {
    Write-Host "🚨 .gitignore dosyası bulunamadı!"
}

# venv git tarafından izleniyorsa kaldır
if (Test-Path "venv") {
    $venvTracked = cmd /c "git ls-files venv/" 2>&1
    if ($venvTracked -and $venvTracked.Count -gt 0) {
        Write-Host "🚨 venv klasörü git tarafından izleniyor! Takipten çıkarılıyor..."
        cmd /c "git rm -r --cached venv/" 2>&1 | Out-Null
        Write-Host "✅ venv takipten çıkarıldı"
    }
}
```

### 3. Lokal Değişiklikleri Kaydet (Stash + Commit)
```powershell
# Önce commitlenmemiş değişiklikleri kontrol et
$status = git status --porcelain 2>&1
if ($status) {
    Write-Host "📝 Değişen dosyalar:"
    git status --short
    git add .
    $tarih = Get-Date -Format "yyyy-MM-dd HH:mm"
    git commit -m "Gun sonu guncellemesi - $tarih (AI-assisted)"
    Write-Host "✅ Lokal değişiklikler commit edildi"
} else {
    Write-Host "ℹ️ Commit edilecek değişiklik yok."
}
```

### 4. Health Check (Push Öncesi Hata Tespiti)
```powershell
if (Test-Path "tests\health_check.py") {
    if (Test-Path "venv\Scripts\python.exe") {
        Write-Host "🔬 Pre-push health check çalıştırılıyor..."
        & venv\Scripts\python tests\health_check.py 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Host "⚠️ Health check uyarıları var ama devam ediyoruz."
        } else {
            Write-Host "✅ Health check başarılı"
        }
    } else {
        Write-Host "⚠️ Python venv bulunamadı. Health check atlanıyor."
        Write-Host "   Çözüm: 'python -m venv venv' ve 'venv\Scripts\pip install -r requirements.txt' çalıştır."
    }
} else {
    Write-Host "ℹ️ Health check scripti bulunamadı, atlanıyor."
}
```

**🤖 AGENT TALİMATI:** Eğer health check **kritik** bir hata gösterirse (örn: `[FAIL]` içeren import hatası):
1. Hatayı düzelt (eksik paket yükle: `& venv\Scripts\pip install -r requirements.txt`)
2. Düzeltmeyi commit'e ekle: `git add .; git commit --amend --no-edit`
3. Kritik olmayan uyarılar (`[WARN]` — GPU yok, Ollama kapalı) için bir şey yapma, devam et.

### 5. Arkadaşların Değişikliklerini Çek (Git Pull)
```powershell
$pullOutput = cmd /c "git pull origin main" 2>&1
Write-Host $pullOutput
```

**🤖 ÇAKIŞMA ÇÖZME TALİMATI (TÜM AI MODELLERİ İÇİN):**

Eğer `git pull` çıktısında **"CONFLICT"** kelimesi varsa, aşağıdaki adımları izle:

1. **Çakışan dosyaları listele:**
   ```powershell
   git diff --name-only --diff-filter=U
   ```

2. **Her çakışan dosya için:**
   - Dosyayı oku (view_file veya cat komutu ile).
   - `<<<<<<<` ile `=======` arası = **BİZİM KOD** (bu bilgisayardaki)
   - `=======` ile `>>>>>>>` arası = **GELEN KOD** (GitHub'dan)

3. **Karar mekanizması (sırasıyla uygula):**
   - **Projeyi BÜTÜNSEL ele al.** Sadece çakışan satırlara değil, dosyanın tamamına ve projenin mantığına bak.
   - İki kod **aynı şeyi farklı şekilde yapıyorsa:** Daha doğru, daha performanslı ve daha güncel olanı seç.
   - İki kod **farklı özellikler ekliyorsa:** İkisini de koru, en iyi şekilde birleştir.
   - İki kodun da **kendine has avantajları varsa:** İkisinin de en iyi kısımlarını al, sentezleyerek yeni ve daha iyi bir versiyon oluştur.
   - **Emin olamıyorsan:** İki kodu da koru ve yorum satırı ekle: `# TODO: Ekip olarak karar verilmeli`

4. **Çakışmayı çözdükten sonra:**
   ```powershell
   git add .
   git commit -m "Merge conflict cozuldu (AI-assisted)"
   ```

5. **Hiç çakışma yoksa** bu adımı atla, devam et.

### 6. Bağımlılık Güncellemesi (Pull Sonrası)
```powershell
# Arkadaş yeni paket eklemiş olabilir — pip ve npm senkronize et
if (Test-Path "venv\Scripts\pip.exe") {
    Write-Host "📦 Python bağımlılıkları kontrol ediliyor..."
    & venv\Scripts\pip install -r requirements.txt --quiet 2>&1 | Out-Null
    Write-Host "✅ Python bağımlılıkları güncel"
}

if (Test-Path "frontend\package.json") {
    $lockBefore = if (Test-Path "frontend\package-lock.json") { (Get-Item "frontend\package-lock.json").LastWriteTime } else { $null }
    $pullChangedFrontend = cmd /c "git diff HEAD~1 --name-only -- frontend/package.json" 2>&1
    if ($pullChangedFrontend -match "package.json") {
        Write-Host "📦 Frontend bağımlılıkları güncelleniyor (package.json değişmiş)..."
        Push-Location frontend
        npm install --silent 2>&1 | Out-Null
        Pop-Location
        Write-Host "✅ Frontend bağımlılıkları güncel"
    }
}
```

### 7. GitHub'a Gönder (Push)
```powershell
$pushOutput = cmd /c "git push origin main" 2>&1
Write-Host $pushOutput
```

**🤖 AGENT TALİMATI:** `git push` komutu PowerShell'de exit code 1 dönebilir — bu bilinen bir PowerShell/stderr sorunudur. Çıktıda **"rejected"** veya **"non-fast-forward"** kelimeleri YOKSA push başarılıdır.

Eğer gerçekten reddedildiyse:
1. Şunu çalıştır: `cmd /c "git pull --rebase origin main" 2>&1`
2. Tekrar dene: `cmd /c "git push origin main" 2>&1`
3. Hâlâ hata varsa, kullanıcıya bildir ve devam et.

### 8. Pinecone Hafıza Senkronizasyonu (Opsiyonel)

> **ÖNEMLİ:** Bu adım SADECE Pinecone MCP ayarlanmış bilgisayarlarda çalışır. Çoğu ekip üyesinde bu kurulu OLMAYACAKTIR — bu tamamen normaldir ve atlanması beklenen bir durumdur.

```powershell
$mcpConfig = "$env:USERPROFILE\.gemini\antigravity\mcp_config.json"
if (Test-Path $mcpConfig) {
    try {
        $config = Get-Content $mcpConfig -Raw | ConvertFrom-Json
        $hasPinecone = $config.mcpServers.PSObject.Properties.Name -contains "pinecone-mcp-server"
        if ($hasPinecone) {
            $scriptPath = "docs\referanslar\ingest_pdfs.py"
            if (Test-Path $scriptPath) {
                Write-Host "🧠 Pinecone Hafıza Güncelleniyor..."
                & venv\Scripts\python $scriptPath --proje-only 2>&1
                Write-Host "✅ Pinecone Hafıza Güncellendi"
            } else {
                Write-Host "ℹ️ ingest_pdfs.py bulunamadı, Pinecone atlanıyor."
            }
        } else {
            Write-Host "ℹ️ Pinecone MCP yapılandırılmamış. (Bu normal, atlanıyor)"
        }
    } catch {
        Write-Host "ℹ️ MCP config okunamadı, Pinecone atlanıyor. (Bu normal)"
    }
} else {
    Write-Host "ℹ️ MCP config bulunamadı. Pinecone atlanıyor. (Bu tamamen normal)"
}
```

### 9. CI/CD Takibi

**🤖 AGENT TALİMATI (TÜM AI MODELLERİ İÇİN):**

Aşağıdaki yöntemlerden birini kullan (hangisi yapılabiliyorsa):

**Yöntem A — Tarayıcı aracın varsa (browser tool):**
1. Tarayıcıyı aç: `https://github.com/cagriaksoy191-oss/structural_health/actions`
2. En son workflow run'ın durumunu kontrol et.
3. ✅ Yeşil tik = Başarılı | ❌ Kırmızı X = Hata | 🟡 Sarı = Çalışıyor

**Yöntem B — Tarayıcı aracın yoksa veya tarayıcı açılamıyorsa (komut satırı):**
```powershell
try {
    $response = Invoke-RestMethod -Uri "https://api.github.com/repos/cagriaksoy191-oss/structural_health/actions/runs?per_page=1" -Method Get -ErrorAction Stop
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
    Write-Host "⚠️ GitHub API'ye erişilemedi. CI/CD durumu manuel kontrol gerektirebilir."
    Write-Host "   URL: https://github.com/cagriaksoy191-oss/structural_health/actions"
}
```

### 10. Canlı Test (Sadece Kontrol — Sunucu Başlatma YOK)

> **NOT:** Bu adım sadece sunucu zaten çalışıyorsa kontrol eder. Gün sonu olduğu için sunucu başlatmaya gerek yok — kullanıcı bilgisayarı kapatacak.

```powershell
$frontendOk = $false
$backendOk = $false

try {
    $web = Invoke-WebRequest -Uri "http://localhost:5173" -TimeoutSec 3 -ErrorAction Stop
    Write-Host "✅ Frontend çalışıyor (HTTP $($web.StatusCode))"
    $frontendOk = $true
} catch {
    Write-Host "ℹ️ Frontend kapalı. (Gün sonu — bu normal)"
}

try {
    $api = Invoke-WebRequest -Uri "http://localhost:8000" -TimeoutSec 3 -ErrorAction Stop
    Write-Host "✅ Backend API çalışıyor"
    $backendOk = $true
} catch {
    Write-Host "ℹ️ Backend kapalı. (Gün sonu — bu normal)"
}

if (-not $frontendOk -and -not $backendOk) {
    Write-Host "ℹ️ Sunucular kapalı — bilgisayar kapatılmaya hazır."
}
```

## Özet Rapor Şablonu
Tüm adımlar bittikten sonra kullanıcıya şu formatta rapor ver:

```
═══════════════════════════════════════
  📋 /GUNSONU RAPORU
═══════════════════════════════════════

  🏃 Runner       : [Aktif / Kurulu Değil]
  🤖 Ollama       : [Açık / Kapalı]
  🔒 .gitignore   : [Güvenli ✅]
  📥 Git Pull     : [Güncel / Çakışma Çözüldü]
  📤 Git Push     : [Başarılı ✅ / Değişiklik Yok]
  🔬 Health Check : [Başarılı / Uyarı Var]
  📦 Bağımlılıklar: [Güncel ✅]
  🧠 Pinecone     : [Güncellendi / Kurulu Değil-Atlandı]
  ⚙️ CI/CD        : [Yeşil ✅ / Çalışıyor / Hata]
  🌐 Sunucu       : [Çalışıyor / Kapalı (normal)]

═══════════════════════════════════════
  ✅ Bilgisayarını kapatabilirsin!
═══════════════════════════════════════
```
