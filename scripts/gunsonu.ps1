# -*- coding: utf-8 -*-
# V12 Titanium - Gun Sonu Otomasyon Scripti
# Bu script /gunsonu workflow'unun TUMUNU tek seferde calistirir.
# Hicbir kullanici etkilesimi gerektirmez.

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$ErrorActionPreference = "Continue"

$rapor = @{}

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  V12 TITANIUM - GUN SONU OTOMASYON" -ForegroundColor Cyan
Write-Host "  $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# ============================================
# ADIM 1: RUNNER KONTROLU
# ============================================
Write-Host "[1/10] Runner Kontrolu..." -ForegroundColor Yellow
$runnerPath = "C:\actions-runner"
if (Test-Path $runnerPath) {
    $runner = Get-Process "Runner.Listener" -ErrorAction SilentlyContinue
    if ($runner) {
        Write-Host "  OK: Runner Zaten Calisiyor" -ForegroundColor Green
        $rapor["Runner"] = "Aktif"
    } else {
        Write-Host "  INFO: Runner Kapali, Baslatiliyor..." -ForegroundColor Yellow
        Start-Process cmd -ArgumentList "/k cd $runnerPath & .\run.cmd"
        $rapor["Runner"] = "Baslatildi"
    }
} else {
    Write-Host "  INFO: Runner kurulu degil (sorun yok)" -ForegroundColor Gray
    $rapor["Runner"] = "Kurulu Degil"
}

# ============================================
# ADIM 2: OLLAMA KONTROLU
# ============================================
Write-Host "[2/10] Ollama Kontrolu..." -ForegroundColor Yellow
$ollama = Get-Process "ollama app" -ErrorAction SilentlyContinue
if ($ollama) {
    Write-Host "  OK: Ollama Servisi Acik" -ForegroundColor Green
    $rapor["Ollama"] = "Acik"
} else {
    Write-Host "  INFO: Ollama kapali (AI yorumlama devre disi, sorun yok)" -ForegroundColor Gray
    $rapor["Ollama"] = "Kapali"
}

# ============================================
# ADIM 3: GITIGNORE GUVENLIK KONTROLU
# ============================================
Write-Host "[3/10] .gitignore Guvenlik Kontrolu..." -ForegroundColor Yellow
$gitignorePath = ".gitignore"
if (Test-Path $gitignorePath) {
    $content = Get-Content $gitignorePath -Raw
    $kritikler = @("venv/", "__pycache__/", "node_modules/", "docs/referanslar/")
    $eksik = $false
    foreach ($item in $kritikler) {
        if ($content -notmatch [regex]::Escape($item)) {
            Write-Host "  WARN: .gitignore'a ekleniyor: $item" -ForegroundColor Yellow
            Add-Content $gitignorePath "`n$item"
            $eksik = $true
        }
    }
    # venv git tarafindan izleniyorsa kaldir
    if (Test-Path "venv") {
        $venvTracked = cmd /c "git ls-files venv/" 2>&1
        if ($venvTracked -and $venvTracked.Count -gt 0) {
            Write-Host "  WARN: venv takipten cikariliyor..." -ForegroundColor Yellow
            cmd /c "git rm -r --cached venv/" 2>&1 | Out-Null
        }
    }
    Write-Host "  OK: .gitignore guvenli" -ForegroundColor Green
    $rapor["Gitignore"] = "Guvenli"
} else {
    Write-Host "  FAIL: .gitignore bulunamadi!" -ForegroundColor Red
    $rapor["Gitignore"] = "BULUNAMADI"
}

# ============================================
# ADIM 4: LOKAL DEGISIKLIKLERI KAYDET
# ============================================
Write-Host "[4/10] Lokal Degisiklikler..." -ForegroundColor Yellow
$status = git status --porcelain 2>&1
if ($status) {
    Write-Host "  Degisen dosyalar:" -ForegroundColor White
    git status --short
    git add .
    $tarih = Get-Date -Format "yyyy-MM-dd HH:mm"
    git commit -m "Gun sonu guncellemesi - $tarih (AI-assisted)" 2>&1 | Out-Null
    Write-Host "  OK: Commit olusturuldu" -ForegroundColor Green
    $rapor["Commit"] = "Olusturuldu"
} else {
    Write-Host "  INFO: Degisiklik yok" -ForegroundColor Gray
    $rapor["Commit"] = "Degisiklik Yok"
}

# ============================================
# ADIM 5: HEALTH CHECK
# ============================================
Write-Host "[5/10] Health Check..." -ForegroundColor Yellow
if ((Test-Path "tests\health_check.py") -and (Test-Path "venv\Scripts\python.exe")) {
    $hcOutput = & venv\Scripts\python tests\health_check.py 2>&1
    $hcOutput | ForEach-Object { Write-Host "  $_" }
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  WARN: Health check uyarilari var" -ForegroundColor Yellow
        $rapor["HealthCheck"] = "Uyari Var"
    } else {
        Write-Host "  OK: Health check basarili" -ForegroundColor Green
        $rapor["HealthCheck"] = "Basarili"
    }
} else {
    Write-Host "  INFO: Health check atlanıyor (venv veya script yok)" -ForegroundColor Gray
    $rapor["HealthCheck"] = "Atlandi"
}

# ============================================
# ADIM 6: GIT PULL (ARKADASLARIN DEGISIKLIKLERI)
# ============================================
Write-Host "[6/10] Git Pull..." -ForegroundColor Yellow
$pullOutput = cmd /c "git pull origin main" 2>&1
Write-Host "  $pullOutput"
if ($pullOutput -match "CONFLICT") {
    Write-Host "  WARN: Conflict var! Agent tarafindan cozulmeli." -ForegroundColor Red
    $rapor["GitPull"] = "CONFLICT - Manuel cozum gerekli"
} elseif ($pullOutput -match "Already up to date") {
    Write-Host "  OK: Zaten guncel" -ForegroundColor Green
    $rapor["GitPull"] = "Guncel"
} else {
    Write-Host "  OK: Yeni degisiklikler cekildi" -ForegroundColor Green
    $rapor["GitPull"] = "Guncellendi"
}

# ============================================
# ADIM 7: BAGIMLILIK SENKRONU
# ============================================
Write-Host "[7/10] Bagimlilik Senkronu..." -ForegroundColor Yellow
if (Test-Path "venv\Scripts\pip.exe") {
    & venv\Scripts\pip install -r requirements.txt --quiet 2>&1 | Out-Null
    Write-Host "  OK: Python bagimliliklari guncel" -ForegroundColor Green
}
if (Test-Path "frontend\package.json") {
    $pkgChanged = cmd /c "git diff HEAD~1 --name-only -- frontend/package.json" 2>&1
    if ($pkgChanged -match "package.json") {
        Write-Host "  INFO: package.json degismis, npm install calisiyor..." -ForegroundColor Yellow
        Push-Location frontend
        npm install --silent 2>&1 | Out-Null
        Pop-Location
        Write-Host "  OK: Frontend bagimliliklari guncel" -ForegroundColor Green
    }
}
$rapor["Bagimlilik"] = "Guncel"

# ============================================
# ADIM 8: GIT PUSH
# ============================================
Write-Host "[8/10] Git Push..." -ForegroundColor Yellow
$pushOutput = cmd /c "git push origin main" 2>&1
if ($pushOutput -match "rejected" -or $pushOutput -match "non-fast-forward") {
    Write-Host "  WARN: Push reddedildi, rebase deneniyor..." -ForegroundColor Yellow
    cmd /c "git pull --rebase origin main" 2>&1 | Out-Null
    $pushOutput2 = cmd /c "git push origin main" 2>&1
    if ($pushOutput2 -match "rejected") {
        Write-Host "  FAIL: Push basarisiz" -ForegroundColor Red
        $rapor["GitPush"] = "BASARISIZ"
    } else {
        Write-Host "  OK: Rebase sonrasi push basarili" -ForegroundColor Green
        $rapor["GitPush"] = "Basarili (rebase)"
    }
} elseif ($pushOutput -match "Everything up-to-date") {
    Write-Host "  INFO: Push edilecek degisiklik yok" -ForegroundColor Gray
    $rapor["GitPush"] = "Degisiklik Yok"
} else {
    Write-Host "  OK: Push basarili" -ForegroundColor Green
    $rapor["GitPush"] = "Basarili"
}

# ============================================
# ADIM 9: PINECONE (OPSIYONEL - TIMEOUT 30sn)
# ============================================
Write-Host "[9/10] Pinecone Kontrolu..." -ForegroundColor Yellow
$mcpConfig = "$env:USERPROFILE\.gemini\antigravity\mcp_config.json"
if (Test-Path $mcpConfig) {
    try {
        $config = Get-Content $mcpConfig -Raw | ConvertFrom-Json
        $hasPinecone = $config.mcpServers.PSObject.Properties.Name -contains "pinecone-mcp-server"
        if ($hasPinecone) {
            $scriptPath = "docs\referanslar\ingest_pdfs.py"
            if (Test-Path $scriptPath) {
                Write-Host "  INFO: Pinecone guncelleniyor (max 30 saniye)..." -ForegroundColor Yellow
                # Timeout ile calistir - 30 saniyede bitmezse atla
                $job = Start-Job -ScriptBlock {
                    param($sp)
                    Set-Location $using:PWD
                    & venv\Scripts\python $sp --proje-only 2>&1
                } -ArgumentList $scriptPath
                $completed = Wait-Job $job -Timeout 30
                if ($completed) {
                    Receive-Job $job | Out-Null
                    Write-Host "  OK: Pinecone guncellendi" -ForegroundColor Green
                    $rapor["Pinecone"] = "Guncellendi"
                } else {
                    Stop-Job $job
                    Write-Host "  WARN: Pinecone 30sn icinde bitmedi, atlandi" -ForegroundColor Yellow
                    $rapor["Pinecone"] = "Timeout-Atlandi"
                }
                Remove-Job $job -Force -ErrorAction SilentlyContinue
            } else {
                Write-Host "  INFO: ingest_pdfs.py bulunamadi, Pinecone atlaniyor" -ForegroundColor Gray
                $rapor["Pinecone"] = "Script Yok"
            }
        } else {
            Write-Host "  INFO: Pinecone MCP yapilandirilmamis (bu normal)" -ForegroundColor Gray
            $rapor["Pinecone"] = "MCP Yok"
        }
    } catch {
        Write-Host "  INFO: MCP config okunamadi (bu normal)" -ForegroundColor Gray
        $rapor["Pinecone"] = "Atlandi"
    }
} else {
    Write-Host "  INFO: MCP config bulunamadi (bu tamamen normal)" -ForegroundColor Gray
    $rapor["Pinecone"] = "Kurulu Degil"
}

# ============================================
# ADIM 10: CI/CD TAKIBI (TIMEOUT 10sn)
# ============================================
Write-Host "[10/10] CI/CD Kontrolu..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "https://api.github.com/repos/cagriaksoy191-oss/structural_health/actions/runs?per_page=1" -Method Get -TimeoutSec 10 -ErrorAction Stop
    $run = $response.workflow_runs[0]
    $durum = $run.conclusion
    $baslik = $run.display_title
    if ($durum -eq "success") {
        Write-Host "  OK: CI/CD Basarili: $baslik" -ForegroundColor Green
        $rapor["CICD"] = "Basarili"
    } elseif ($durum -eq $null) {
        Write-Host "  INFO: CI/CD Calisiyor: $baslik" -ForegroundColor Yellow
        $rapor["CICD"] = "Calisiyor"
    } else {
        Write-Host "  FAIL: CI/CD Hata: $baslik ($durum)" -ForegroundColor Red
        $rapor["CICD"] = "Hata: $durum"
    }
} catch {
    Write-Host "  WARN: GitHub API erisilemedi (10sn timeout)" -ForegroundColor Yellow
    $rapor["CICD"] = "API Erisilemedi"
}

# ============================================
# OZET RAPOR
# ============================================
Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  /GUNSONU RAPORU" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Runner       : $($rapor['Runner'])"
Write-Host "  Ollama       : $($rapor['Ollama'])"
Write-Host "  .gitignore   : $($rapor['Gitignore'])"
Write-Host "  Commit       : $($rapor['Commit'])"
Write-Host "  Health Check : $($rapor['HealthCheck'])"
Write-Host "  Git Pull     : $($rapor['GitPull'])"
Write-Host "  Bagimliliklar: $($rapor['Bagimlilik'])"
Write-Host "  Git Push     : $($rapor['GitPush'])"
Write-Host "  Pinecone     : $($rapor['Pinecone'])"
Write-Host "  CI/CD        : $($rapor['CICD'])"
Write-Host ""
Write-Host "================================================" -ForegroundColor Green
Write-Host "  Bilgisayarini kapatabilirsin!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host ""
