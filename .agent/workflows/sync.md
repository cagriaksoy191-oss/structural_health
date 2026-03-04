---
description: Gün içi ekip farkındalık kontrolü — remote değişiklik var mı?
---

# /sync - Gün İçi Farkındalık Kontrolü

Bu workflow **SALT OKUNUR** çalışır. Lokal dosyalarınıza dokunmaz, pull yapmaz, merge etmez.
Sadece ekip arkadaşlarınızın sizden sonra kod pushlayıp pushlamadığını kontrol eder.

> **AGENT TALİMATI:** Aşağıdaki komutu çalıştır. Çıktıyı oku ve kullanıcıya raporla. Bu komut **HİÇBİR ŞEYİ DEĞİŞTİRMEZ**, sadece bilgi verir.

// turbo-all

## Çalıştır

```powershell
Write-Host ""; Write-Host "=== /SYNC - Remote Kontrol ===" -ForegroundColor Cyan; $fetchOut = cmd /c "git fetch origin main" 2>&1; $count = (cmd /c "git rev-list HEAD..origin/main --count" 2>&1).Trim(); if ($count -match "^\d+$") { $count = [int]$count } else { $count = -1 }; if ($count -eq 0) { Write-Host ""; Write-Host "  Sistem guncel. Ekip arkadaslarindan gelen yeni bir degisiklik yok," -ForegroundColor Green; Write-Host "  guvenle kod yazmaya devam edebilirsin." -ForegroundColor Green } elseif ($count -gt 0) { Write-Host ""; Write-Host "  DIKKAT: Remote repository sende olmayan $count adet yeni commit iceriyor." -ForegroundColor Red; Write-Host "  Ekip arkadaslarin kod pushlamis!" -ForegroundColor Red; Write-Host ""; Write-Host "  Son $count commit:" -ForegroundColor Yellow; $logs = cmd /c "git log HEAD..origin/main --oneline" 2>&1; foreach ($l in $logs) { Write-Host "    $l" -ForegroundColor Yellow }; Write-Host ""; Write-Host "  Kodlamaya devam etmeden once cakismalari onlemek icin" -ForegroundColor Yellow; Write-Host "  kodlarini kaydedip /gunsonu komutunu calistirmayi dusunebilirsin." -ForegroundColor Yellow } else { Write-Host "  Remote kontrol basarisiz. Internet baglantisini kontrol et." -ForegroundColor Red }; Write-Host ""; Write-Host "===============================" -ForegroundColor Cyan; Write-Host ""
```

## Ne Yapar?

1. `git fetch origin main` — Remote'daki son durumu indirir (**merge yapmaz**)
2. `git rev-list HEAD..origin/main --count` — Sende olmayan commit sayısını sayar
3. Eğer yeni commit var ise son commit listesini gösterir

## Ne YAPMAZ?

- ❌ `git pull` yapmaz
- ❌ `git merge` yapmaz
- ❌ `git stash` almaz
- ❌ Lokal dosyalarınıza dokunmaz
- ❌ AGENTS.md veya progress.md'yi değiştirmez

## Beklenen Çıktı (Güncel)

```
=== /SYNC - Remote Kontrol ===

  Sistem guncel. Ekip arkadaslarindan gelen yeni bir degisiklik yok,
  guvenle kod yazmaya devam edebilirsin.

===============================
```

## Beklenen Çıktı (Yeni Commit Var)

```
=== /SYNC - Remote Kontrol ===

  DIKKAT: Remote repository sende olmayan 3 adet yeni commit iceriyor.
  Ekip arkadaslarin kod pushlamis!

  Son 3 commit:
    a1b2c3d Gun sonu guncellemesi - 2026-03-05 18:15 (AI-assisted)
    d4e5f6g AFAD API timeout fix
    h7i8j9k Frontend BOM fix

  Kodlamaya devam etmeden once cakismalari onlemek icin
  kodlarini kaydedip /gunsonu komutunu calistirmayi dusunebilirsin.

===============================
```
