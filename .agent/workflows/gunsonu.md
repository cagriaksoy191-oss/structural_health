---
description: Gün Sonu (End of Day) - Full CI/CD Döngüsü
---

# /gunsonu - Tam Otomatik CI/CD Akışı

Bu workflow, gün sonunda yapılması gereken tüm işlemleri (Runner kontrolü, Git senkronizasyonu, Test ve Push) tek seferde halleder.

## Adımlar

### 1. Runner Kontrolü
// turbo
```powershell
$runner = Get-Process "Runner.Listener" -ErrorAction SilentlyContinue
if ($runner) {
    Write-Host "✅ Runner Zaten Çalışıyor"
} else {
    Write-Host "⚠️ Runner Kapalı, Başlatılıyor..."
    Start-Process cmd -ArgumentList "/k cd C:\actions-runner & .\run.cmd"
}
```

### 2. Değişiklikleri Çek (Pull) ve Birleştir
```powershell
git pull origin main
```
**🤖 MANTIKLI BİRLEŞTİRME TALİMATI (AGENT İÇİN):**
Eğer `git pull` sırasında "CONFLICT" (Çakışma) oluşursa:
1.  Çakışan dosyaları aç (`<<<<<<<`, `=======`, `>>>>>>>` işaretlerini bul).
2.  Arkadaşının ve senin kodunu karşılaştır.
3.  **Mantıklı olanı seç** veya ikisini birleştir (Sadece bir tarafı silip atma, projenin bütünlüğünü koru).
4.  Neden bu kararı verdiğini kullanıcıya kısaca açıkla.
5.  `git add` ve `git commit` ile birleştirmeyi tamamla.

### 3. Değişiklikleri Gönder (Push)
Eğer değişiklik varsa gönder:
```powershell
git add .
git commit -m "Gun sonu guncellemesi (Automated by Antigravity)"
git push origin main
```
*(Not: Eğer "nothing to commit" derse sorun yok, devam et.)*

### 4. CI/CD Takibi
GitHub Actions'ın tetiklendiğini ve başarılı olduğunu doğrula.
1.  Tarayıcıyı aç ve şu adrese git: `https://github.com/cagriaksoy191-oss/structural_health/actions`
2.  En son çalışan işin (Workflow) durumunu kontrol et.
3.  Yeşil tik ✅ almasını bekle (veya devam ettiğini gör).

### 5. Canlı Test (Browser)
Projenin son halini lokalde test et:
1.  Tarayıcıda `http://localhost:5173` adresini aç.
2.  Ana sayfanın (Formun) doğru yüklendiğini gör.
3.  Rastgele verilerle "Hesapla" butonuna bas.
4.  Sonuç ekranının hatasız geldiğini doğrula.

## Beklenen Sonuç
```
✅ Runner: Aktif
✅ Git: Güncel ve Pushlandı (Çakışmalar çözüldü)
✅ CI/CD: Kontrol Edildi
✅ Test: Sorunsuz çalışıyor
```
