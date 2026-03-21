# scripts/sabah_rutini.ps1
# /sabah workflow - Hash-tabanli akilli bagimlilik kontrolu
# Kullanim: powershell -ExecutionPolicy Bypass -File scripts\sabah_rutini.ps1
# -------------------------------------------------------------------

$ErrorActionPreference = "Continue"

# =============================================
# DIZIN GUVENLIK KONTROLU
# =============================================
# Script sadece proje kok dizininden calistirilmali
$requiredFiles = @("main.py", "requirements.txt", "AGENTS.md")
foreach ($f in $requiredFiles) {
    if (-not (Test-Path $f)) {
        Write-Host "HATA: '$f' bulunamadi. Bu script proje kok dizininden calistirilmalidir." -ForegroundColor Red
        Write-Host "Beklenen dizin: git root (main.py, requirements.txt, AGENTS.md icermeli)" -ForegroundColor Red
        exit 1
    }
}
Write-Host "Dizin dogrulandi: $(Get-Location)" -ForegroundColor DarkGray

# =============================================
# 1. GIT PULL
# =============================================
Write-Host ""
Write-Host "--- 1. Git Pull ---" -ForegroundColor Cyan
$pullOutput = cmd /c "git pull origin main" 2>&1
Write-Host $pullOutput

if ($pullOutput -match "CONFLICT") {
    Write-Host "UYAR: Merge conflict tespit edildi! Agent cozum uygulayacak." -ForegroundColor Yellow
    # Agent talimat: conflict coz, raporla, commit et
}

# =============================================
# CACHE YARDIMCI FONKSIYONLARI
# =============================================
$cacheFile = ".sabah_cache"

function Get-FileHashValue($filePath) {
    if (Test-Path $filePath) {
        return (Get-FileHash -Path $filePath -Algorithm SHA256).Hash
    }
    return $null
}

function Read-SabahCache {
    if (Test-Path $cacheFile) {
        try {
            return (Get-Content $cacheFile -Raw | ConvertFrom-Json)
        }
        catch {
            return $null
        }
    }
    return $null
}

function Write-SabahCache($reqHash, $pkgHash) {
    $cache = @{
        requirements_hash = $reqHash
        package_json_hash = $pkgHash
        last_updated      = (Get-Date -Format "yyyy-MM-ddTHH:mm:ss")
    }
    $cache | ConvertTo-Json | Set-Content $cacheFile -Encoding UTF8
}

# =============================================
# 2. AKILLI BAGIMLILIK KONTROLU
# =============================================
Write-Host ""
Write-Host "--- 2. Bagimlilik Kontrolu ---" -ForegroundColor Cyan

# Cache ve hash'leri oku
$cache = Read-SabahCache
$currentReqHash = Get-FileHashValue "requirements.txt"
$currentPkgHash = Get-FileHashValue "frontend\package.json"
$cachedReqHash = if ($cache) { $cache.requirements_hash } else { $null }
$cachedPkgHash = if ($cache) { $cache.package_json_hash } else { $null }

# --- PYTHON ---
$venvPath = $null
if (Test-Path ".venv\Scripts\python.exe") {
    $venvPath = ".venv"
} elseif (Test-Path "venv\Scripts\python.exe") {
    $venvPath = "venv"
}

if ($null -eq $venvPath) {
    Write-Host "[HATA] Sanal ortam bozuk veya eksik (-Scripts\python.exe- bulunamadi)." -ForegroundColor Red
    Write-Host "Lutfen projeyi baslatmadan once kurulum.bat dosyasini calistirin." -ForegroundColor Yellow
    exit 1
}

Write-Host "Python venv mevcut ($venvPath algilandi)" -ForegroundColor Green

# Saglik Kontrolu (Proxy Import)
$healthCheckCmd = 'import fastapi, torch, skfuzzy, supabase, httpx, dotenv'
$null = & "$venvPath\Scripts\python.exe" -c $healthCheckCmd 2>&1
$healthOk = ($LASTEXITCODE -eq 0)

$forcePip = $false
if (-not $healthOk) {
    Write-Host "UYARI: Temsili paketler eksik veya bozuk! Hash bypass ediliyor." -ForegroundColor Yellow
    $forcePip = $true
}

if (-not $forcePip -and ($currentReqHash -eq $cachedReqHash)) {
    $shortHash = $currentReqHash.Substring(0, 12)
    Write-Host "requirements.txt degismemis (hash: $shortHash), pip install atlaniyor" -ForegroundColor Green
}
else {
    if ($forcePip -and ($currentReqHash -eq $cachedReqHash)) {
        Write-Host "Eksik kutuphane tespit edildi, pip zorlaniyor..." -ForegroundColor Yellow
    } else {
        Write-Host "requirements.txt degismis, bagimliliklar guncelleniyor..." -ForegroundColor Yellow
    }
    
    & "$venvPath\Scripts\python.exe" -m pip install -r requirements.txt --progress-bar off 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Python bagimliliklari guncellendi" -ForegroundColor Green
    }
    else {
        Write-Host "pip install basarisiz! (exit code: $LASTEXITCODE)" -ForegroundColor Red
        Write-Host "Cache guncellenmedi, sonraki calistirmada tekrar denenecek" -ForegroundColor Yellow
        $currentReqHash = $cachedReqHash
    }
}

# --- FRONTEND ---
if (Test-Path "frontend\package.json") {
    Push-Location frontend
    if (-not (Test-Path "node_modules")) {
        Write-Host "Frontend node_modules kuruluyor (ilk kurulum)..." -ForegroundColor Yellow
        npm install --loglevel warn 2>&1
        Write-Host "Frontend bagimliliklari kuruldu" -ForegroundColor Green
    }
    elseif ($currentPkgHash -ne $cachedPkgHash) {
        Write-Host "package.json degismis, npm install calistiriliyor..." -ForegroundColor Yellow
        npm install --loglevel warn 2>&1
        Write-Host "Frontend bagimliliklari guncellendi" -ForegroundColor Green
    }
    else {
        Write-Host "Frontend bagimliliklari guncel (package.json degismemis)" -ForegroundColor Green
    }
    Pop-Location
}

# --- CACHE GUNCELLE ---
Write-SabahCache $currentReqHash $currentPkgHash

# =============================================
# 3. DURUM RAPORU
# =============================================
Write-Host ""
Write-Host "--- 3. Durum Raporu ---" -ForegroundColor Cyan
Write-Host "Git pull: Tamamlandi" -ForegroundColor Green
Write-Host "Python venv: Hazir" -ForegroundColor Green
Write-Host "Cache: Guncellendi (.sabah_cache)" -ForegroundColor Green
Write-Host "Calismaya hazirsin!" -ForegroundColor Green
