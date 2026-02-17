# ============================================================
#  /GUNSONU - Tam Otomatik CI/CD Script
#  4 kisilik ekipte herkesin bilgisayarinda sorunsuz calisir.
#  Hicbir ozel araca (Pinecone, Ollama, Runner) bagli degildir.
#  Eksik olanlar otomatik atlanir.
# ============================================================

$ErrorActionPreference = "Continue"

# Rapor degiskenleri
$rapor = @{
    Runner       = "Kontrol edilmedi"
    Ollama       = "Kontrol edilmedi"
    Gitignore    = "Kontrol edilmedi"
    Commit       = "Kontrol edilmedi"
    HealthCheck  = "Kontrol edilmedi"
    GitPull      = "Kontrol edilmedi"
    Bagimliliklar = "Kontrol edilmedi"
    GitPush      = "Kontrol edilmedi"
    Pinecone     = "Kontrol edilmedi"
    CICD         = "Kontrol edilmedi"
}

Write-Host ""
Write-Host "================================================"
Write-Host "  /GUNSONU BASLATILIYOR..."
Write-Host "================================================"
Write-Host ""

# ----------------------------------------------------------
# 1. RUNNER KONTROLU
# ----------------------------------------------------------
Write-Host "[1/10] Runner Kontrolu..."
try {
    $runnerPath = "C:\actions-runner"
    Write-Host "  >> Runner yolu kontrol ediliyor: $runnerPath"
    if (Test-Path $runnerPath) {
        Write-Host "  >> Runner klasoru bulundu."
        $runner = Get-Process "Runner.Listener" -ErrorAction SilentlyContinue
        if ($runner) {
            Write-Host "  >> Runner Zaten Calisiyor"
            $rapor.Runner = "Aktif"
        } else {
            if (Test-Path "$runnerPath\run.cmd") {
                Write-Host "  >> Runner Kapali, Baslatiliyor..."
                Start-Process cmd -ArgumentList "/k cd $runnerPath & .\run.cmd"
                $rapor.Runner = "Baslatildi"
            } else {
                Write-Host "  >> Runner klasoru bos veya run.cmd yok."
                $rapor.Runner = "Eksik Dosya"
            }
        }
    } else {
        Write-Host "  >> Bu bilgisayarda Runner kurulu degil (Klasor yok). (Sorun yok)"
        $rapor.Runner = "Kurulu Degil"
    }
} catch {
    Write-Host "  >> Runner kontrol hatasi: $($_.Exception.Message)"
    $rapor.Runner = "Hata"
}

# ----------------------------------------------------------
# 2. OLLAMA KONTROLU
# ----------------------------------------------------------
Write-Host "[2/10] Ollama Kontrolu..."
try {
    $ollama = Get-Process "ollama app" -ErrorAction SilentlyContinue
    if ($ollama) {
        Write-Host "  >> Ollama Servisi Acik"
        try {
            $models = ollama list 2>&1
            if ($models -match "qwen") {
                Write-Host "  >> Qwen Modeli Yuklu"
                $rapor.Ollama = "Acik (Qwen yuklu)"
            } else {
                Write-Host "  >> Qwen modeli bulunamadi"
                $rapor.Ollama = "Acik (Qwen yok)"
            }
        } catch {
            $rapor.Ollama = "Acik (model kontrol edilemedi)"
        }
    } else {
        Write-Host "  >> Ollama kapali veya yuklu degil. (Sorun yok)"
        $rapor.Ollama = "Kapali"
    }
} catch {
    Write-Host "  >> Ollama kontrol hatasi: $($_.Exception.Message)"
    $rapor.Ollama = "Hata"
}

# ----------------------------------------------------------
# 3. .GITIGNORE GUVENLIK KONTROLU
# ----------------------------------------------------------
Write-Host "[3/10] .gitignore Guvenlik Kontrolu..."
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
    } else {
        Write-Host "  >> .gitignore bulunamadi!"
        $rapor.Gitignore = "DOSYA YOK!"
    }
} catch {
    Write-Host "  >> .gitignore hatasi: $($_.Exception.Message)"
    $rapor.Gitignore = "Hata"
}

# ----------------------------------------------------------
# 4. LOKAL COMMIT
# ----------------------------------------------------------
Write-Host "[4/10] Lokal Commit..."
try {
    $status = git status --porcelain 2>&1
    if ($status) {
        Write-Host "  >> Degisen dosyalar var, commit olusturuluyor..."
        git add . 2>&1 | Out-Null
        $tarih = Get-Date -Format "yyyy-MM-dd HH:mm"
        $commitOutput = git commit -m "Gun sonu guncellemesi - $tarih (AI-assisted)" 2>&1
        Write-Host "  >> $commitOutput"
        $rapor.Commit = "Olusturuldu"
    } else {
        Write-Host "  >> Commit edilecek degisiklik yok."
        $rapor.Commit = "Degisiklik Yok"
    }
} catch {
    Write-Host "  >> Commit hatasi: $($_.Exception.Message)"
    $rapor.Commit = "Hata"
}

# ----------------------------------------------------------
# 5. HEALTH CHECK
# ----------------------------------------------------------
Write-Host "[5/10] Health Check..."
try {
    if (Test-Path "tests\health_check.py") {
        if (Test-Path "venv\Scripts\python.exe") {
            $hcOutput = & venv\Scripts\python tests\health_check.py 2>&1
            Write-Host "  >> $hcOutput"
            if ($LASTEXITCODE -ne 0) {
                $rapor.HealthCheck = "Uyari Var"
            } else {
                $rapor.HealthCheck = "Basarili"
            }
        } else {
            Write-Host "  >> venv bulunamadi, health check atlanıyor."
            $rapor.HealthCheck = "venv Yok"
        }
    } else {
        Write-Host "  >> health_check.py bulunamadi, atlaniyor."
        $rapor.HealthCheck = "Script Yok"
    }
} catch {
    Write-Host "  >> Health check hatasi: $($_.Exception.Message)"
    $rapor.HealthCheck = "Hata"
}

# ----------------------------------------------------------
# 6. GIT PULL (Arkadaslarin Degisiklikleri)
# ----------------------------------------------------------
Write-Host "[6/10] Git Pull..."
try {
    $pullOutput = cmd /c "git pull origin main" 2>&1
    Write-Host "  >> $pullOutput"
    if ($pullOutput -match "CONFLICT") {
        Write-Host "  >> CONFLICT TESPIT EDILDI! Agent conflict cozmelidir."
        $rapor.GitPull = "CONFLICT VAR"
    } elseif ($pullOutput -match "Already up to date") {
        $rapor.GitPull = "Guncel"
    } else {
        $rapor.GitPull = "Guncellendi"
    }
} catch {
    Write-Host "  >> Git pull hatasi: $($_.Exception.Message)"
    $rapor.GitPull = "Hata"
}

# ----------------------------------------------------------
# 7. BAGIMLILIK SENKRONIZASYONU
# ----------------------------------------------------------
Write-Host "[7/10] Bagimlilik Senkronizasyonu..."
try {
    # Python bagimliliklari
    if (Test-Path "venv\Scripts\pip.exe") {
        if (Test-Path "requirements.txt") {
            & venv\Scripts\pip install -r requirements.txt --quiet 2>&1 | Out-Null
            Write-Host "  >> Python bagimliliklari senkronize edildi"
        }
    }
    # Frontend bagimliliklari
    if (Test-Path "frontend\package.json") {
        Push-Location frontend
        if (-not (Test-Path "node_modules")) {
            Write-Host "  >> Frontend node_modules kuruluyor..."
            npm install --silent 2>&1 | Out-Null
        } else {
            Write-Host "  >> Frontend node_modules mevcut"
        }
        Pop-Location
    }
    $rapor.Bagimliliklar = "Guncel"
} catch {
    Write-Host "  >> Bagimlilik hatasi: $($_.Exception.Message)"
    $rapor.Bagimliliklar = "Hata"
}

# ----------------------------------------------------------
# 8. GIT PUSH
# ----------------------------------------------------------
Write-Host "[8/10] Git Push..."
try {
    # Pull sonrasi yeni commit olabilir, kontrol et
    $status2 = git status --porcelain 2>&1
    if ($status2) {
        git add . 2>&1 | Out-Null
        $tarih2 = Get-Date -Format "yyyy-MM-dd HH:mm"
        git commit -m "Post-pull guncelleme - $tarih2 (AI-assisted)" 2>&1 | Out-Null
    }

    $pushOutput = cmd /c "git push origin main" 2>&1
    Write-Host "  >> $pushOutput"

    if ($pushOutput -match "rejected" -or $pushOutput -match "non-fast-forward") {
        Write-Host "  >> Push reddedildi, rebase deneniyor..."
        cmd /c "git pull --rebase origin main" 2>&1 | Out-Null
        $pushOutput2 = cmd /c "git push origin main" 2>&1
        Write-Host "  >> $pushOutput2"
        if ($pushOutput2 -match "rejected") {
            $rapor.GitPush = "BASARISIZ"
        } else {
            $rapor.GitPush = "Basarili (rebase ile)"
        }
    } else {
        $rapor.GitPush = "Basarili"
    }
} catch {
    Write-Host "  >> Git push hatasi: $($_.Exception.Message)"
    $rapor.GitPush = "Hata"
}

# ----------------------------------------------------------
# 9. PINECONE HAFIZA (Akilli Senkronizasyon)
# ----------------------------------------------------------
Write-Host "[9/10] Pinecone Hafiza Kontrolu..."
try {
    $syncScript = "scripts\smart_sync.py"
    if ((Test-Path $syncScript) -and (Test-Path "venv\Scripts\python.exe")) {
        Write-Host "  >> Akilli hafiza senkronizasyonu baslatiliyor..."
        
        # Scripti calistir
        $process = Start-Process -FilePath "venv\Scripts\python.exe" -ArgumentList $syncScript -NoNewWindow -PassThru -Wait
        
        if ($process.ExitCode -eq 0) {
            Write-Host "  >> Hafiza senkronizasyonu tamamlandi."
            $rapor.Pinecone = "Guncellendi"
        } else {
            Write-Host "  >> Senkronizasyon hatasi veya degisiklik yok (ExitCode: $($process.ExitCode))."
            Write-Host "  >> .env dosyasinda PINECONE_API_KEY oldugundan emin olun."
            $rapor.Pinecone = "Hata/Atlandi"
        }
    } else {
        Write-Host "  >> smart_sync.py veya venv bulunamadi. Atlanıyor."
        $rapor.Pinecone = "Script Yok"
    }
} catch {
    Write-Host "  >> Pinecone islem hatasi: $($_.Exception.Message)"
    $rapor.Pinecone = "Hata"
}

# ----------------------------------------------------------
# 10. CI/CD TAKIBI (GitHub API - Private Repo Destekli)
# ----------------------------------------------------------
Write-Host "[10/10] CI/CD Takibi..."
try {
    # TLS 1.2 zorunlu (eski Windows sürümlerinde gerekli)
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

    $apiUrl = "https://api.github.com/repos/cagriaksoy191-oss/structural_health/actions/runs?per_page=1"
    $headers = @{ "User-Agent" = "StructuralHealth-CI" }

    # Git credential manager'dan token cikar (private repo destegi)
    try {
        $tokenLine = ("protocol=https`nhost=github.com`n" | git credential fill 2>$null | Select-String "password=")
        if ($tokenLine) {
            $token = ($tokenLine -split "password=")[1].Trim()
            if ($token) {
                $headers["Authorization"] = "token $token"
            }
        }
    } catch {
        # Token alinamazsa devam et (public repo'larda gerek yok)
    }

    $response = Invoke-RestMethod -Uri $apiUrl -Method Get -TimeoutSec 15 -Headers $headers -ErrorAction Stop
    $run = $response.workflow_runs[0]
    $durum = $run.conclusion
    $baslik = $run.display_title

    if ($durum -eq "success") {
        Write-Host "  >> CI/CD Basarili: $baslik"
        $rapor.CICD = "Basarili"
    } elseif ($null -eq $durum) {
        Write-Host "  >> CI/CD Calisiyor: $baslik"
        $rapor.CICD = "Calisiyor"
    } else {
        Write-Host "  >> CI/CD Hata: $baslik (Durum: $durum)"
        $rapor.CICD = "Hata: $durum"
    }
} catch {
    Write-Host "  >> GitHub API erisilemedi: $($_.Exception.Message)"
    Write-Host "  >> Tarayicida kontrol edebilirsin: https://github.com/cagriaksoy191-oss/structural_health/actions"
    $rapor.CICD = "Manuel Kontrol Gerekli"
}

# ----------------------------------------------------------
# OZET RAPOR
# ----------------------------------------------------------
Write-Host ""
Write-Host "================================================"
Write-Host "  /GUNSONU RAPORU"
Write-Host "================================================"
Write-Host ""
Write-Host "  Runner       : $($rapor.Runner)"
Write-Host "  Ollama       : $($rapor.Ollama)"
Write-Host "  .gitignore   : $($rapor.Gitignore)"
Write-Host "  Commit       : $($rapor.Commit)"
Write-Host "  Health Check : $($rapor.HealthCheck)"
Write-Host "  Git Pull     : $($rapor.GitPull)"
Write-Host "  Bagimliliklar: $($rapor.Bagimliliklar)"
Write-Host "  Git Push     : $($rapor.GitPush)"
Write-Host "  Pinecone     : $($rapor.Pinecone)"
Write-Host "  CI/CD        : $($rapor.CICD)"
Write-Host ""
Write-Host "================================================"
Write-Host "  Bilgisayarini kapatabilirsin!"
Write-Host "================================================"
Write-Host ""
