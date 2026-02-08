---
description: Gün Sonu (End of Day) - Full CI/CD Döngüsü
---

# /gunsonu - Tam Otomatik CI/CD Akışı

Bu workflow, gün sonunda yapılması gereken tüm işlemleri (Runner kontrolü, Git senkronizasyonu, Test ve Push) tek seferde halleder.

## Adımlar

### 1. Runner Kontrolü (Sadece Kuruluysa)
// turbo
```powershell
$runnerPath = "C:\actions-runner"
if (Test-Path $runnerPath) {
    $runner = Get-Process "Runner.Listener" -ErrorAction SilentlyContinue
    if ($runner) {
        Write-Host "✅ Runner Zaten Çalışıyor"
    } else {
        Write-Host "⚠️ Runner Kapalı, Başlatılıyor..."
        Start-Process cmd -ArgumentList "/k cd $runnerPath & .\run.cmd"
    }
} else {
    Write-Host "ℹ️ Bu bilgisayarda GitHub Runner kurulu değil. (Bu adım atlanıyor, sorun yok)"
}
```

### 2. Git Güvenlik Kontrolü (VENV Koruması)
// turbo
```powershell
$gitignore = Get-Content .gitignore
if ($gitignore -notcontains "venv/") {
    Write-Host "⚠️ DIKKAT: .gitignore dosyasında venv eksik! Ekleniyor..."
    Add-Content .gitignore "`nvenv/"
}
if (Test-Path "venv") {
    $venvStatus = git status --porcelain venv/
    if ($venvStatus) {
        Write-Host "🚨 KRITIK: venv klasörü git tarafından izleniyor! Takipten çıkarılıyor..."
        git rm -r --cached venv/
    }
}
```

### 3. Değişiklikleri Çek (Pull) ve Birleştir
```powershell
git pull origin main
```
**🤖 MANTIKLI BİRLEŞTİRME TALİMATI (AGENT İÇİN):**
Eğer `git pull` sırasında "CONFLICT" (Çakışma) oluşursa:
1.  Çakışan dosyaları aç.
2.  Mantıklı olanı seç veya birleştir (Silip atma).
3.  `git add` ve `git commit` ile tamamla.

### 4. Değişiklikleri Gönder (Push)
```powershell
git add .
git commit -m "Gun sonu guncellemesi (Automated by Antigravity)"
git push origin main
```

### 5. CI/CD Takibi
GitHub Actions'ın tetiklendiğini ve başarılı olduğunu doğrula.
1.  Tarayıcıyı aç ve şu adrese git: `https://github.com/cagriaksoy191-oss/structural_health/actions`
2.  En son çalışan işin (Workflow) durumunu kontrol et.
3.  Yeşil tik ✅ almasını bekle (veya devam ettiğini gör).

### 6. Canlı Test (Sunucu Kontrolü ile)
Projenin son halini lokalde test et.
**🤖 AGENT TALİMATI:**
1.  Önce `http://localhost:5173` adresini kontrol et.
2.  **Eğer sayfa açılmazsa (Bağlantı Hatası):**
    *   `baslat.bat` dosyasını çalıştır (Start-Process ile).
    *   15 saniye bekle (Sunucunun açılması için).
    *   Tekrar kontrol et.
3.  **Hala açılmıyorsa:** "Sunucu başlatılamadı" diye rapor ver ama işlemi durdurma (GitHub testi zaten başarılı).
4.  **Açılırsa:** Formu doldur, "Hesapla" butonuna bas ve sonucu gör.

## Beklenen Sonuç
```
✅ Runner: Aktif
✅ Git: Güncel ve Pushlandı (Venv koruması aktif)
✅ CI/CD: Kontrol Edildi (Yeşil)
✅ Test: Sunucu kontrol edildi ve test yapıldı
```
