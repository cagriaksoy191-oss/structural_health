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
    if (Test-Path $runnerPath) {
        $runner = Get-Process "Runner.Listener" -ErrorAction SilentlyContinue
        if ($runner) {
            Write-Host "  >> Runner Zaten Calisiyor"
            $rapor.Runner = "Aktif"
        } else {
            Write-Host "  >> Runner Kapali, Baslatiliyor..."
            Start-Process cmd -ArgumentList "/k cd $runnerPath & .\run.cmd"
            $rapor.Runner = "Baslatildi"
        }
    } else {
        Write-Host "  >> Bu bilgisayarda Runner kurulu degil. (Sorun yok)"
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
# 9. PINECONE HAFIZA (Opsiyonel - Sadece Kurulanlar Icin)
# ----------------------------------------------------------
Write-Host "[9/10] Pinecone Kontrolu..."
try {
    $mcpConfig = "$env:USERPROFILE\.gemini\antigravity\mcp_config.json"
    if (Test-Path $mcpConfig) {
        $config = Get-Content $mcpConfig -Raw | ConvertFrom-Json
        $hasPinecone = $config.mcpServers.PSObject.Properties.Name -contains "pinecone-mcp-server"
        if ($hasPinecone) {
            $scriptPath = "docs\referanslar\ingest_pdfs.py"
            if ((Test-Path $scriptPath) -and (Test-Path "venv\Scripts\python.exe")) {
                Write-Host "  >> Pinecone Hafiza Guncelleniyor (30sn timeout)..."
                $job = Start-Job -ScriptBlock {
                    param($sp)
                    Set-Location $using:PWD
                    & venv\Scripts\python $sp --proje-only 2>&1
                } -ArgumentList $scriptPath
                $completed = Wait-Job $job -Timeout 30
                if ($completed) {
                    $jobOutput = Receive-Job $job
                    Write-Host "  >> $jobOutput"
                    $rapor.Pinecone = "Guncellendi"
                } else {
                    Stop-Job $job
                    Write-Host "  >> Pinecone timeout (30sn), atlaniyor."
                    $rapor.Pinecone = "Timeout"
                }
                Remove-Job $job -Force -ErrorAction SilentlyContinue
            } else {
                Write-Host "  >> ingest_pdfs.py veya venv bulunamadi, Pinecone atlaniyor."
                $rapor.Pinecone = "Script Yok"
            }
        } else {
            Write-Host "  >> Pinecone MCP yapilandirilmamis. (Bu normal)"
            $rapor.Pinecone = "Kurulu Degil"
        }
    } else {
        Write-Host "  >> MCP config bulunamadi. Pinecone atlaniyor. (Bu tamamen normal)"
        $rapor.Pinecone = "Kurulu Degil"
    }
} catch {
    Write-Host "  >> Pinecone hatasi: $($_.Exception.Message) (Bu normal, atlaniyor)"
    $rapor.Pinecone = "Atlandi"
}

# ----------------------------------------------------------
# 10. CI/CD TAKIBI (GitHub API)
# ----------------------------------------------------------
Write-Host "[10/10] CI/CD Takibi..."
try {
    $response = Invoke-RestMethod -Uri "https://api.github.com/repos/cagriaksoy191-oss/structural_health/actions/runs?per_page=1" -Method Get -TimeoutSec 10 -ErrorAction Stop
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
    Write-Host "  >> GitHub API'ye erisilemedi. (Internet veya rate limit)"
    $rapor.CICD = "API Hatasi"
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
