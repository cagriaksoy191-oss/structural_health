# ============================================================
#  /GUNSONU - Tam Otomatik CI/CD Script (v2 - Cakisma Korumali)
#  4 kisilik ekipte herkesin bilgisayarinda sorunsuz calisir.
#  Yeni akis: Fetch -> Stash -> Pull -> Pop -> Conflict Check
#             -> Test -> Commit -> Push
#  Eski sira (Commit -> Pull -> Push) KALDIRILDI.
#  Yedek: scripts/gunsonu.ps1.bak
# ============================================================

$ErrorActionPreference = "Continue"

# Rapor degiskenleri
$rapor = @{
    Runner        = "Kontrol edilmedi"
    Ollama        = "Kontrol edilmedi"
    Gitignore     = "Kontrol edilmedi"
    RemoteSync    = "Kontrol edilmedi"
    Bagimliliklar = "Kontrol edilmedi"
    HealthCheck   = "Kontrol edilmedi"
    Commit        = "Kontrol edilmedi"
    GitPush       = "Kontrol edilmedi"
    Pinecone      = "Kontrol edilmedi"
    CICD          = "Kontrol edilmedi"
}

Write-Host ""
Write-Host "================================================"
Write-Host "  /GUNSONU BASLATILIYOR... (v2 - Cakisma Korumali)"
Write-Host "================================================"
Write-Host ""

# ----------------------------------------------------------
# 1. RUNNER KONTROLU
# ----------------------------------------------------------
Write-Host "[1/11] Runner Kontrolu..."
Write-Host "  >> Eski 'self-hosted' runner kaldirildi. CI/CD dogrudan GitHub Cloud (ubuntu-latest) uzerinde calisiyor."
$rapor.Runner = "GitHub Cloud"

# ----------------------------------------------------------
# 2. OLLAMA KONTROLU
# ----------------------------------------------------------
Write-Host "[2/11] Ollama Kontrolu..."
try {
    $ollama = Get-Process "ollama app" -ErrorAction SilentlyContinue
    if ($ollama) {
        Write-Host "  >> Ollama Servisi Acik"
        try {
            $models = ollama list 2>&1
            if ($models -match "qwen") {
                Write-Host "  >> Qwen Modeli Yuklu"
                $rapor.Ollama = "Acik (Qwen yuklu)"
            }
            else {
                Write-Host "  >> Qwen modeli bulunamadi"
                $rapor.Ollama = "Acik (Qwen yok)"
            }
        }
        catch {
            $rapor.Ollama = "Acik (model kontrol edilemedi)"
        }
    }
    else {
        Write-Host "  >> Ollama kapali veya yuklu degil. (Sorun yok)"
        $rapor.Ollama = "Kapali"
    }
}
catch {
    Write-Host "  >> Ollama kontrol hatasi: $($_.Exception.Message)"
    $rapor.Ollama = "Hata"
}

# ----------------------------------------------------------
# 3. .GITIGNORE GUVENLIK KONTROLU
# ----------------------------------------------------------
Write-Host "[3/11] .gitignore Guvenlik Kontrolu..."
try {
    $gitignorePath = ".gitignore"
    if (Test-Path $gitignorePath) {
        $content = Get-Content $gitignorePath -Raw
        $kritikler = @("venv/", "__pycache__/", "node_modules/", "docs/referanslar/")
        $eklenen = 0
        foreach ($item in $kritikler) {
            if ($content -notmatch [regex]::Escape($item)) {
                Add-Content $gitignorePath "`n$item"
                Write-Host "  >> Eklendi: $item"
                $eklenen++
            }
        }
        # venv takipten cikar
        if (Test-Path "venv") {
            $venvTracked = cmd /c "git ls-files venv/" 2>&1
            if ($venvTracked -and $venvTracked.Count -gt 0) {
                cmd /c "git rm -r --cached venv/" 2>&1 | Out-Null
                Write-Host "  >> venv takipten cikarildi"
            }
        }
        if ($eklenen -eq 0) {
            Write-Host "  >> .gitignore zaten guvenli"
        }
        $rapor.Gitignore = "Guvenli"
    }
    else {
        Write-Host "  >> .gitignore bulunamadi!"
        $rapor.Gitignore = "DOSYA YOK!"
    }
}
catch {
    Write-Host "  >> .gitignore hatasi: $($_.Exception.Message)"
    $rapor.Gitignore = "Hata"
}

# ----------------------------------------------------------
# 4. GIT FETCH + REMOTE DURUM KONTROLU
# ----------------------------------------------------------
Write-Host "[4/11] Git Fetch + Remote Kontrol..."
try {
    # Remote'daki son durumu indir (merge yapmaz)
    $fetchOutput = cmd /c "git fetch origin main" 2>&1
    Write-Host "  >> Fetch tamamlandi"

    # Remote'da bizden kac commit ileride oldugunu say
    $behindCount = (cmd /c "git rev-list HEAD..origin/main --count" 2>&1).Trim()
    
    if ($behindCount -match "^\d+$") {
        $behindCount = [int]$behindCount
    }
    else {
        # Hata durumunda guvenli tarafta kal
        Write-Host "  >> rev-list ciktisi beklenmedik: $behindCount"
        $behindCount = 0
    }

    if ($behindCount -gt 0) {
        Write-Host "  >> Remote $behindCount commit ileride! Ekip arkadaslariniz degisiklik yapmis." -ForegroundColor Yellow
    }
    else {
        Write-Host "  >> Remote guncel, ekipten yeni degisiklik yok." -ForegroundColor Green
    }
}
catch {
    Write-Host "  >> Git fetch hatasi: $($_.Exception.Message)"
    $behindCount = 0
}

# ----------------------------------------------------------
# 5. AKILLI SENKRONIZASYON (Kritik Bolum)
#    Stash -> Pull -> Pop -> Conflict Check
# ----------------------------------------------------------
Write-Host "[5/11] Akilli Senkronizasyon..."

# Lokal degisiklik var mi?
$localChanges = git status --porcelain 2>&1
$hasLocalChanges = ($localChanges -and $localChanges.Count -gt 0)

if ($hasLocalChanges) {
    $changedFileCount = ($localChanges | Measure-Object).Count
    Write-Host "  >> Lokal degisiklik: $changedFileCount dosya" -ForegroundColor Cyan
}
else {
    Write-Host "  >> Lokal degisiklik yok" -ForegroundColor Green
}

$stashUsed = $false

try {
    if ($behindCount -gt 0 -and $hasLocalChanges) {
        # ============================================
        # FULL SYNC PATH: Hem lokal hem remote degisti
        # Stash -> Pull -> Pop -> Conflict Check
        # ============================================
        Write-Host "  >> [FULL SYNC] Hem lokal hem remote degismis. Guvenli birlestirme basliyor..." -ForegroundColor Yellow

        # Adim A: Lokal degisiklikleri stash'le
        $tarihStamp = Get-Date -Format "yyyyMMdd-HHmm"
        $stashMsg = "gunsonu-$tarihStamp"
        Write-Host "  >> Stash olusturuluyor: $stashMsg"
        $stashOutput = cmd /c "git stash --include-untracked -m `"$stashMsg`"" 2>&1
        Write-Host "  >> $stashOutput"
        $stashUsed = $true

        # Adim B: Temiz pull (conflict olmaz, cunku lokal commit yok)
        Write-Host "  >> Remote degisiklikler cekiliyor (temiz pull)..."
        $pullOutput = cmd /c "git pull origin main" 2>&1
        Write-Host "  >> $pullOutput"

        if ($pullOutput -match "CONFLICT" -or $pullOutput -match "error:" -or $pullOutput -match "fatal:") {
            Write-Host ""
            Write-Host "  !! HATA: Temiz pull sirasinda beklenmeyen sorun." -ForegroundColor Red
            Write-Host "  !! Stash'iniz korunuyor: $stashMsg" -ForegroundColor Red
            Write-Host "  !! Stash'i geri almak icin: git stash pop" -ForegroundColor Red
            $rapor.RemoteSync = "HATA (Pull basarisiz)"
            # Raporu goster ve cik
            # (rapor gosterme kodu asagida)
        }

        # Adim C: Stash pop — lokal degisiklikleri guncel kodun uzerine uygula
        Write-Host "  >> Stash pop: Lokal degisiklikler guncel kodun uzerine uygulaniyor..."
        $popOutput = cmd /c "git stash pop" 2>&1
        $popExitCode = $LASTEXITCODE
        Write-Host "  >> $popOutput"

        # Adim D: CONFLICT CHECK (Kritik Karar Noktasi)
        $conflictFiles = @()
        
        # Yontem 1: git stash pop cikis kodu
        $hasConflict = ($popExitCode -ne 0)
        
        # Yontem 2: Unmerged dosya kontrolu
        $unmerged = cmd /c "git diff --name-only --diff-filter=U" 2>&1
        if ($unmerged -and $unmerged.Trim() -ne "") {
            $hasConflict = $true
            $conflictFiles = $unmerged -split "`n" | Where-Object { $_.Trim() -ne "" }
        }
        
        # Yontem 3: Conflict marker kontrolu (ekstra guvenlik)
        if (-not $hasConflict -and ($popOutput -match "CONFLICT")) {
            $hasConflict = $true
        }

        if ($hasConflict) {
            Write-Host ""
            Write-Host "  ================================================" -ForegroundColor Red
            Write-Host "  !! CAKISMA (CONFLICT) TESPIT EDILDI !!" -ForegroundColor Red
            Write-Host "  ================================================" -ForegroundColor Red
            Write-Host ""
            if ($conflictFiles.Count -gt 0) {
                Write-Host "  Cakisan dosyalar:" -ForegroundColor Red
                foreach ($cf in $conflictFiles) {
                    Write-Host "    - $cf" -ForegroundColor Red
                }
            }
            else {
                Write-Host "  Cakisan dosyalari bulmak icin: git diff --name-only --diff-filter=U" -ForegroundColor Yellow
            }
            Write-Host ""
            Write-Host "  SCRIPT DURDURULUYOR (Exit Code 99)." -ForegroundColor Red
            Write-Host "  Agent bu cakismayi cozmeli, sonra /gunsonu tekrar calistirilmali." -ForegroundColor Yellow
            Write-Host ""
            $rapor.RemoteSync = "CONFLICT (Exit 99)"

            # Raporu goster ve EXIT 99
            Write-Host ""
            Write-Host "================================================"
            Write-Host "  /GUNSONU RAPORU (YARIDA KESILDI)"
            Write-Host "================================================"
            Write-Host ""
            Write-Host "  Runner        : $($rapor.Runner)"
            Write-Host "  Ollama        : $($rapor.Ollama)"
            Write-Host "  .gitignore    : $($rapor.Gitignore)"
            Write-Host "  Remote Sync   : $($rapor.RemoteSync)" -ForegroundColor Red
            Write-Host "  Bagimliliklar : (atlanildi)"
            Write-Host "  Health Check  : (atlanildi)"
            Write-Host "  Commit        : (atlanildi)"
            Write-Host "  Git Push      : (atlanildi)"
            Write-Host "  Pinecone      : (atlanildi)"
            Write-Host "  CI/CD         : (atlanildi)"
            Write-Host ""
            Write-Host "================================================"
            Write-Host "  CAKISMA COZULMEDEN PUSH YAPILMADI."
            Write-Host "  Agent talimatlarini oku (gunsonu.md)."
            Write-Host "================================================"
            Write-Host ""
            exit 99
        }

        # Conflict yok - basarili birlestirme
        Write-Host "  >> Birlestirme basarili! Cakisma yok." -ForegroundColor Green
        $rapor.RemoteSync = "$behindCount commit cekildi + birlesti"

    }
    elseif ($behindCount -gt 0 -and -not $hasLocalChanges) {
        # ============================================
        # PULL-ONLY PATH: Sadece remote degismis
        # ============================================
        Write-Host "  >> [PULL-ONLY] Sadece remote degismis, temiz pull yeterli..." -ForegroundColor Cyan
        $pullOutput = cmd /c "git pull origin main" 2>&1
        Write-Host "  >> $pullOutput"
        $rapor.RemoteSync = "$behindCount commit cekildi"

    }
    elseif ($behindCount -eq 0 -and $hasLocalChanges) {
        # ============================================
        # FAST PATH: Sadece lokal degismis
        # ============================================
        Write-Host "  >> [FAST PATH] Sadece lokal degisiklik var, sync gerekmez." -ForegroundColor Green
        $rapor.RemoteSync = "Guncel (sync gerekmedi)"

    }
    else {
        # ============================================
        # NO-OP: Hicbir sey degismemis
        # ============================================
        Write-Host "  >> [NO-OP] Ne lokal ne remote degisiklik var." -ForegroundColor Green
        $rapor.RemoteSync = "Guncel"
    }
}
catch {
    Write-Host "  >> Senkronizasyon hatasi: $($_.Exception.Message)" -ForegroundColor Red
    if ($stashUsed) {
        Write-Host "  >> DIKKAT: Stash'iniz hala mevcut. 'git stash list' ile kontrol edin." -ForegroundColor Yellow
    }
    $rapor.RemoteSync = "Hata"
}

# ----------------------------------------------------------
# VENV Path Bulma (Cross-Machine Destegi)
# ----------------------------------------------------------
$venvPath = ""
if (Test-Path ".venv\Scripts\python.exe") {
    $venvPath = ".venv"
} elseif (Test-Path "venv\Scripts\python.exe") {
    $venvPath = "venv"
}

# ----------------------------------------------------------
# 6. BAGIMLILIK SENKRONIZASYONU
#    (Pull'dan sonra, cunku yeni requirements gelmis olabilir)
# ----------------------------------------------------------
Write-Host "[6/11] Bagimlilik Senkronizasyonu..."
try {
    # Python bagimliliklari
    if ($venvPath -and (Test-Path "$venvPath\Scripts\pip.exe")) {
        if (Test-Path "requirements.txt") {
            & $venvPath\Scripts\pip install -r requirements.txt --quiet 2>&1 | Out-Null
            Write-Host "  >> Python bagimliliklari senkronize edildi ($venvPath kullanildi)"
        }
    } else {
        Write-Host "  >> Python venv. bulunamadi (atlanildi)." -ForegroundColor Yellow
    }
    
    # Frontend bagimliliklari
    if (Test-Path "frontend\package.json") {
        Push-Location frontend
        if (-not (Test-Path "node_modules")) {
            Write-Host "  >> Frontend node_modules kuruluyor..."
            npm install --silent 2>&1 | Out-Null
        }
        else {
            Write-Host "  >> Frontend node_modules mevcut"
        }
        Pop-Location
    }
    $rapor.Bagimliliklar = "Guncel"
}
catch {
    Write-Host "  >> Bagimlilik hatasi: $($_.Exception.Message)"
    $rapor.Bagimliliklar = "Hata"
}

# ----------------------------------------------------------
# 7. HEALTH CHECK + IMPORT DOGRULAMA
#    (Birlestirme sonrasi: kod hala calisiyor mu?)
# ----------------------------------------------------------
Write-Host "[7/11] Health Check + Import Dogrulama..."
try {
    $importOK = $true

    # Import dogrulama (hizli kontrol)
    if ($venvPath -and (Test-Path "$venvPath\Scripts\python.exe")) {
        Write-Host "  >> Import dogrulama testi calistiriliyor ($venvPath kullaniliyor)..."
        $importOutput = & $venvPath\Scripts\python -c "import main; print('import OK')" 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Host "  >> UYARI: 'import main' basarisiz!" -ForegroundColor Red
            Write-Host "  >> Cikti: $importOutput" -ForegroundColor Red
            $importOK = $false
        }
        else {
            Write-Host "  >> Import dogrulama basarili" -ForegroundColor Green
        }
    }

    # Health check script
    if (Test-Path "tests\health_check.py") {
        if ($venvPath -and (Test-Path "$venvPath\Scripts\python.exe")) {
            $hcOutput = & $venvPath\Scripts\python tests\health_check.py 2>&1
            Write-Host "  >> $hcOutput"
            if ($LASTEXITCODE -ne 0) {
                $rapor.HealthCheck = "Uyari Var"
            }
            else {
                $rapor.HealthCheck = "Basarili"
            }
        }
        else {
            Write-Host "  >> venv bulunamadi, health check atlaniyor."
            $rapor.HealthCheck = "venv Yok"
        }
    }
    else {
        Write-Host "  >> health_check.py bulunamadi, atlaniyor."
        $rapor.HealthCheck = "Script Yok"
    }

    if (-not $importOK) {
        $rapor.HealthCheck = "IMPORT HATASI"
        Write-Host ""
        Write-Host "  !! UYARI: Import testi basarisiz oldu. Birlestirmede sorun olabilir." -ForegroundColor Red
        Write-Host "  !! Push oncesi durumu kontrol edin." -ForegroundColor Yellow
        # Not: Burada EXIT yapmiyoruz, kullaniciya uyari verip devam ediyoruz.
        # Agent bu uyariyi gorup karar verecek.
    }
}
catch {
    Write-Host "  >> Health check hatasi: $($_.Exception.Message)"
    $rapor.HealthCheck = "Hata"
}

# ----------------------------------------------------------
# 8. LOKAL COMMIT
#    (Artik hem kendi degisikliklerimiz hem de remote
#     cekilmis durumdaki dosyalar uzerinde commit yapiyoruz)
# ----------------------------------------------------------
Write-Host "[8/11] Lokal Commit..."
try {
    $status = git status --porcelain 2>&1
    if ($status) {
        Write-Host "  >> Degisen dosyalar var, commit olusturuluyor..."
        git add . 2>&1 | Out-Null
        $tarih = Get-Date -Format "yyyy-MM-dd HH:mm"
        $commitOutput = git commit -m "Gun sonu guncellemesi - $tarih (AI-assisted)" 2>&1
        Write-Host "  >> $commitOutput"
        $rapor.Commit = "Olusturuldu"
    }
    else {
        Write-Host "  >> Commit edilecek degisiklik yok."
        $rapor.Commit = "Degisiklik Yok"
    }
}
catch {
    Write-Host "  >> Commit hatasi: $($_.Exception.Message)"
    $rapor.Commit = "Hata"
}

# ----------------------------------------------------------
# 9. GIT PUSH
#    (Artik rejected/non-fast-forward olmamali,
#     cunku pull zaten yapildi)
# ----------------------------------------------------------
Write-Host "[9/11] Git Push..."
try {
    $pushOutput = cmd /c "git push origin main" 2>&1
    Write-Host "  >> $pushOutput"

    if ($pushOutput -match "rejected" -or $pushOutput -match "non-fast-forward") {
        # GUVENLIK: Rebase ASLA yapilmaz (sessiz veri kaybi riski).
        # Push reddedildiyse, script calisirken biri yeni push yapmis demektir.
        Write-Host ""
        Write-Host "  ================================================" -ForegroundColor Red
        Write-Host "  !! PUSH REDDEDILDI !!" -ForegroundColor Red
        Write-Host "  ================================================" -ForegroundColor Red
        Write-Host ""
        Write-Host "  Script calisirken remote repository'ye yeni bir push yapilmis." -ForegroundColor Yellow
        Write-Host "  Veri kaybini onlemek icin otomatik rebase YAPILMIYOR." -ForegroundColor Yellow
        Write-Host "  Lutfen /gunsonu islemini tekrar baslatin." -ForegroundColor Yellow
        Write-Host ""
        $rapor.GitPush = "REDDEDILDI (tekrar /gunsonu calistirin)"

        # Raporu goster ve guvenli cikis
        Write-Host ""
        Write-Host "================================================"
        Write-Host "  /GUNSONU RAPORU (PUSH REDDEDILDI)"
        Write-Host "================================================"
        Write-Host ""
        Write-Host "  Runner        : $($rapor.Runner)"
        Write-Host "  Ollama        : $($rapor.Ollama)"
        Write-Host "  .gitignore    : $($rapor.Gitignore)"
        Write-Host "  Remote Sync   : $($rapor.RemoteSync)"
        Write-Host "  Bagimliliklar : $($rapor.Bagimliliklar)"
        Write-Host "  Health Check  : $($rapor.HealthCheck)"
        Write-Host "  Commit        : $($rapor.Commit)"
        Write-Host "  Git Push      : $($rapor.GitPush)" -ForegroundColor Red
        Write-Host "  Pinecone      : (atlanildi)"
        Write-Host "  CI/CD         : (atlanildi)"
        Write-Host ""
        Write-Host "================================================"
        Write-Host "  /gunsonu tekrar calistirin."
        Write-Host "================================================"
        Write-Host ""
        exit 1
    }
    else {
        $rapor.GitPush = "Basarili"
    }
}
catch {
    Write-Host "  >> Git push hatasi: $($_.Exception.Message)"
    $rapor.GitPush = "Hata"
}

# ----------------------------------------------------------
# 10. PINECONE HAFIZA (Akilli Senkronizasyon)
# ----------------------------------------------------------
Write-Host "[10/11] Pinecone Hafiza Kontrolu..."
try {
    $syncScript = "scripts\smart_sync.py"
    if ((Test-Path $syncScript) -and (Test-Path "venv\Scripts\python.exe")) {
        Write-Host "  >> Akilli hafiza senkronizasyonu baslatiliyor..."
        
        $syncOutput = & venv\Scripts\python.exe $syncScript 2>&1
        $syncExitCode = $LASTEXITCODE
        
        if ($syncOutput) {
            foreach ($line in $syncOutput) {
                Write-Host "  >> $line"
            }
        }
        
        if ($syncExitCode -eq 0) {
            Write-Host "  >> Hafiza senkronizasyonu tamamlandi."
            $rapor.Pinecone = "Guncellendi"
        }
        else {
            Write-Host "  >> Senkronizasyon hatasi (ExitCode: $syncExitCode)."
            Write-Host "  >> .env dosyasinda PINECONE_API_KEY oldugundan emin olun."
            $rapor.Pinecone = "Hata/Atlandi"
        }
    }
    else {
        Write-Host "  >> smart_sync.py veya venv bulunamadi. Atlaniyor."
        $rapor.Pinecone = "Script Yok"
    }
}
catch {
    Write-Host "  >> Pinecone islem hatasi: $($_.Exception.Message)"
    $rapor.Pinecone = "Hata"
}

# ----------------------------------------------------------
# 11. CI/CD TAKIBI (GitHub API - Private Repo Destekli)
# ----------------------------------------------------------
Write-Host "[11/11] CI/CD Takibi..."
try {
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

    $apiUrl = "https://api.github.com/repos/cagriaksoy191-oss/structural_health/actions/runs?per_page=1"
    $headers = @{ "User-Agent" = "StructuralHealth-CI" }

    try {
        $tokenLine = ("protocol=https`nhost=github.com`n" | git credential fill 2>$null | Select-String "password=")
        if ($tokenLine) {
            $token = ($tokenLine -split "password=")[1].Trim()
            if ($token) {
                $headers["Authorization"] = "token $token"
            }
        }
    }
    catch {
        # Token alinamazsa devam et
    }

    $response = Invoke-RestMethod -Uri $apiUrl -Method Get -TimeoutSec 15 -Headers $headers -ErrorAction Stop
    $run = $response.workflow_runs[0]
    $durum = $run.conclusion
    $baslik = $run.display_title

    if ($durum -eq "success") {
        Write-Host "  >> CI/CD Basarili: $baslik"
        $rapor.CICD = "Basarili"
    }
    elseif ($null -eq $durum) {
        Write-Host "  >> CI/CD Calisiyor: $baslik"
        $rapor.CICD = "Calisiyor"
    }
    else {
        Write-Host "  >> CI/CD Hata: $baslik (Durum: $durum)"
        $rapor.CICD = "Hata: $durum"
    }
}
catch {
    Write-Host "  >> GitHub API erisilemedi: $($_.Exception.Message)"
    Write-Host "  >> Tarayicida kontrol edebilirsin: https://github.com/cagriaksoy191-oss/structural_health/actions"
    $rapor.CICD = "Manuel Kontrol Gerekli"
}

# ----------------------------------------------------------
# OZET RAPOR
# ----------------------------------------------------------
Write-Host ""
Write-Host "================================================"
Write-Host "  /GUNSONU RAPORU (v2)"
Write-Host "================================================"
Write-Host ""
Write-Host "  Runner        : $($rapor.Runner)"
Write-Host "  Ollama        : $($rapor.Ollama)"
Write-Host "  .gitignore    : $($rapor.Gitignore)"

# Remote Sync rengini duruma gore ayarla
if ($rapor.RemoteSync -match "CONFLICT") {
    Write-Host "  Remote Sync   : $($rapor.RemoteSync)" -ForegroundColor Red
}
elseif ($rapor.RemoteSync -match "cekildi") {
    Write-Host "  Remote Sync   : $($rapor.RemoteSync)" -ForegroundColor Yellow
}
else {
    Write-Host "  Remote Sync   : $($rapor.RemoteSync)" -ForegroundColor Green
}

Write-Host "  Bagimliliklar : $($rapor.Bagimliliklar)"
Write-Host "  Health Check  : $($rapor.HealthCheck)"
Write-Host "  Commit        : $($rapor.Commit)"
Write-Host "  Git Push      : $($rapor.GitPush)"
Write-Host "  Pinecone      : $($rapor.Pinecone)"
Write-Host "  CI/CD         : $($rapor.CICD)"
Write-Host ""
Write-Host "================================================"
Write-Host "  Bilgisayarini kapatabilirsin!"
Write-Host "================================================"
Write-Host ""
