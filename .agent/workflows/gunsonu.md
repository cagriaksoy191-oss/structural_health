---
description: Gün Sonu (End of Day) - Full CI/CD Döngüsü
---

# /gunsonu - Tam Otomatik CI/CD Akışı

Bu workflow, gün sonunda yapılması gereken **TÜM** işlemleri tek seferde halleder.
4 kişilik ekipte herkesin bilgisayarında sorunsuz çalışır.

> **ÖNEMLİ AGENT TALİMATI:** Bu workflow tamamen self-contained (bağımsız). Hiçbir harici bilgiye, geçmiş konuşma hafızasına veya MCP sunucusuna ihtiyaç duymaz. Her adımı sırasıyla çalıştır. Bir adım başarısız olursa durma — hata mesajını kaydet ve bir sonraki adıma geç. En sonda özet raporu ver. Bu talimatlar tüm AI modelleri (Claude, GPT, Gemini, vb.) tarafından anlaşılabilecek şekilde yazılmıştır.

// turbo-all

## Adımlar

### 1. Runner Kontrolü (Sadece Kuruluysa)
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
    Write-Host "ℹ️ Bu bilgisayarda GitHub Runner kurulu değil. (Sorun yok, atlanıyor)"
}
```

### 2. Ollama (Yapay Zeka) Kontrolü
```powershell
$ollama = Get-Process "ollama app" -ErrorAction SilentlyContinue
if ($ollama) {
    Write-Host "✅ Ollama Servisi Açık"
    try {
        $models = ollama list 2>&1
        if ($models -match "qwen") {
            Write-Host "✅ Qwen Modeli Yüklü"
        } else {
            Write-Host "⚠️ UYARI: Qwen modeli bulunamadı. AI yorumlama devre dışı olabilir."
        }
    } catch {
        Write-Host "⚠️ Ollama list komutu çalıştırılamadı."
    }
} else {
    Write-Host "ℹ️ Ollama kapalı veya yüklü değil. (AI yorumlama devre dışı kalabilir, sorun yok)"
}
```

### 3. .gitignore Güvenlik Kontrolü
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

### 4. Arkadaşların Değişikliklerini Çek (Git Pull)
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
   - Dosyayı aç ve `<<<<<<<`, `=======`, `>>>>>>>` işaretlerini bul.
   - `<<<<<<<` ile `=======` arası = **BİZİM KOD** (bu bilgisayardaki)
   - `=======` ile `>>>>>>>` arası = **GELEN KOD** (GitHub'dan)

3. **Karar mekanizması (sırasıyla uygula):**
   - İki kod **aynı şeyi farklı şekilde yapıyorsa:** Daha doğru/güncel olanı seç.
   - İki kod **farklı özellikler ekliyorsa:** İkisini de koru, birleştir.
   - **Emin olamıyorsan:** İki kodu da koru ve yorum satırı ekle: `# TODO: Ekip olarak karar verilmeli`

4. **Çakışmayı çözdükten sonra:**
   ```powershell
   git add .
   git commit -m "Merge conflict cozuldu (AI-assisted)"
   ```

5. **Hiç çakışma yoksa** bu adımı atla, devam et.

### 5. Değişiklikleri Kontrol Et ve Commitle
```powershell
$status = git status --porcelain 2>&1
if ($status) {
    Write-Host "📝 Değişen dosyalar:"
    git status --short
    git add .
    $tarih = Get-Date -Format "yyyy-MM-dd HH:mm"
    git commit -m "Gun sonu guncellemesi - $tarih (AI-assisted)"
    Write-Host "✅ Commit oluşturuldu"
} else {
    Write-Host "ℹ️ Commit edilecek değişiklik yok."
}
```

### 6. Health Check (Push Öncesi Hata Tespiti)
```powershell
if (Test-Path "tests\health_check.py") {
    Write-Host "🔬 Pre-push health check çalıştırılıyor..."
    & venv\Scripts\python tests\health_check.py 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "⚠️ Health check uyarıları var. Commit yine de gönderilecek."
    } else {
        Write-Host "✅ Health check başarılı"
    }
} else {
    Write-Host "ℹ️ Health check scripti bulunamadı, atlanıyor."
}
```

**🤖 AGENT TALİMATI:** Eğer health check **kritik** bir hata gösterirse (örn: import hatası):
1. Hatayı düzelt (eksik paket yükle, syntax hatasını düzelt, vb.)
2. Düzeltmeyi commit'e ekle: `git add . && git commit --amend --no-edit`
3. Kritik olmayan uyarılar (GPU yok, Ollama kapalı) için bir şey yapma, devam et.

### 7. GitHub'a Gönder (Push)
```powershell
$pushOutput = cmd /c "git push origin main" 2>&1
Write-Host $pushOutput
```
**🤖 AGENT TALİMATI:** Eğer push reddedilirse ("rejected", "non-fast-forward"):
1. Şunu çalıştır: `cmd /c "git pull --rebase origin main" 2>&1`
2. Tekrar dene: `cmd /c "git push origin main" 2>&1`
3. Hâlâ hata varsa, kullanıcıya bildir ve devam et (CI/CD'ye geç)

### 8. Pinecone Hafıza Senkronizasyonu (Opsiyonel - Sadece Kurulanlar İçin)

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

**Yöntem B — Tarayıcı aracın yoksa (komut satırı):**
```powershell
# GitHub API ile son workflow durumunu kontrol et
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

### 10. Canlı Test (Sunucu Kontrolü)

**🤖 AGENT TALİMATI (TÜM AI MODELLERİ İÇİN):**

Aşağıdaki yöntemlerden birini kullan (hangisi yapılabiliyorsa):

**Yöntem A — Tarayıcı aracın varsa:**
1. `http://localhost:5173` adresini tarayıcıda aç.
2. Sayfa açılıyorsa → "Canlı test başarılı" raporla.
3. Açılmıyorsa → Yöntem B'deki komutu çalıştır.

**Yöntem B — Her türlü AI modeli için çalışır:**
```powershell
# Önce frontend'in çalışıp çalışmadığını kontrol et
try {
    $web = Invoke-WebRequest -Uri "http://localhost:5173" -TimeoutSec 5 -ErrorAction Stop
    Write-Host "✅ Frontend çalışıyor (HTTP $($web.StatusCode))"
} catch {
    Write-Host "⚠️ Frontend kapalı. Başlatılıyor..."
    if (Test-Path "baslat.bat") {
        Start-Process "baslat.bat"
        Start-Sleep -Seconds 15
        # Tekrar kontrol
        try {
            $web2 = Invoke-WebRequest -Uri "http://localhost:5173" -TimeoutSec 5 -ErrorAction Stop
            Write-Host "✅ Frontend başlatıldı ve çalışıyor"
        } catch {
            Write-Host "⚠️ Frontend başlatılamadı. Manuel kontrol gerekli."
        }
    } else {
        Write-Host "ℹ️ baslat.bat bulunamadı. Sunucu manuel başlatılmalı."
    }
}

# Backend kontrolü
try {
    $api = Invoke-WebRequest -Uri "http://localhost:8000" -TimeoutSec 5 -ErrorAction Stop
    Write-Host "✅ Backend API çalışıyor"
} catch {
    Write-Host "⚠️ Backend API kapalı veya henüz başlamadı."
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
  🧠 Pinecone     : [Güncellendi / Kurulu Değil-Atlandı]
  ⚙️ CI/CD        : [Yeşil ✅ / Çalışıyor / Hata]
  🌐 Canlı Test   : [Başarılı / Sunucu Kapalı]

═══════════════════════════════════════
  ✅ Bilgisayarını kapatabilirsin!
═══════════════════════════════════════
```
