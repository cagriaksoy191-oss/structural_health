# Antigravity Olmadan CI/CD Kullanımı

Bu rehber, Antigravity IDE **kullanmayanlar** için günlük rutin adımlarını açıklar.

---

## 🕐 NE ZAMAN NE YAPILIR?

| Zaman | Yapılacak İş |
|-------|-------------|
| **Sabah, bilgisayarı açınca** | Son değişiklikleri çek |
| **Kod yazıp bitirince** | Değişiklikleri GitHub'a gönder |
| **Gönderdikten sonra** | Testin geçip geçmediğini kontrol et |

---

## 1️⃣ SABAH - Günü Başlat

PowerShell aç ve şunları yaz:

```powershell
cd C:\Users\SENIN_KULLANICI_ADIN\structural_health
git pull origin main
.\venv\Scripts\Activate
```

✅ `(venv)` yazısı görünürse hazırsın!

---

## 2️⃣ KOD BİTİNCE - GitHub'a Gönder

```powershell
git add .
git commit -m "Ne yaptığını buraya yaz"
git push origin main
```

✅ "main -> main" yazısı görünürse gönderildi!

---

## 3️⃣ KONTROL - Test Sonucunu Gör

Tarayıcıda şu linki aç:
```
https://github.com/cagriaksoy191-oss/structural_health/actions
```

- ✅ **Yeşil tik** = Her şey yolunda
- ❌ **Kırmızı çarpı** = Hata var, düzelt ve tekrar gönder

---

## 📊 ÖZET

```
SABAH:    cd proje → git pull → venv aktif
KOD BİTTİ: git add → git commit → git push
KONTROL:   GitHub Actions sayfasına bak
```

---

---

# 🔧 EKSTRALAR (Sadece Gerektiğinde)

## /test - Lokal Test

**Ne Zaman:** Göndermeden önce çalışıyor mu diye denemek istersen.

```powershell
cd C:\Users\SENIN_KULLANICI_ADIN\structural_health
.\venv\Scripts\Activate
py -3.11 tests/health_check.py
```

✅ "All checks passed" görürsen sorun yok.

---

## /runner - Runner Başlat

**Ne Zaman:** Bilgisayarı yeniden başlattıysan ve testler "beklemede" kalıyorsa.

```powershell
C:\actions-runner\run.cmd
```

✅ "Listening for Jobs" yazısı görünürse çalışıyor.

**Not:** Runner'ı sadece **bir kişi** (genelde Çağrı) çalıştıracak. Herkesin çalıştırmasına gerek yok.

---

## ❓ SIKÇA SORULAN SORULAR

**S: Her sabah runner başlatmam gerekiyor mu?**
C: Hayır. Runner zaten açıksa bir şey yapmana gerek yok.

**S: git push yazınca hata aldım, ne yapayım?**
C: Önce `git pull origin main` yaz, sonra tekrar `git push origin main` dene.

**S: Antigravity'de `/gonder` yazsam olmuyor mu?**
C: Antigravity varsa evet, `/gonder` yeterli. Bu dosya Antigravity **olmayanlar** için.

---

*Son Güncelleme: 6 Şubat 2026*
