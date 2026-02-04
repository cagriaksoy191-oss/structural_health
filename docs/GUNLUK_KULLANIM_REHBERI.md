# 📅 V12 Titanium - Günlük Kullanım Rehberi
## Her Gün Projede Çalışmak İçin Yapman Gerekenler

---

# ☀️ SABAH - BİLGİSAYARI AÇTIĞINDA

## ADIM 1: Runner'ı Başlat (CI/CD için)

### Ne yapacaksın?
GitHub'dan gelen test komutlarını alan programı başlatacaksın.

### Nasıl yapacaksın?

**1.** Windows tuşuna bas

**2.** "PowerShell" yaz

**3.** "Windows PowerShell" uygulamasına tıkla

**4.** Şu komutu yaz ve Enter'a bas:
```
C:\actions-runner\run.cmd
```

**5.** Şunu görmelisin:
```
√ Connected to GitHub
Listening for Jobs
```

**6.** ⚠️ **ÖNEMLİ:** Bu pencereyi KAPATMA! Açık kalsın.

---

## ADIM 2: En Son Değişiklikleri Al

### Ne yapacaksın?
Arkadaşların değişiklik yapmış olabilir. Onları kendi bilgisayarına çekeceksin.

### Nasıl yapacaksın?

**1.** YENİ bir PowerShell penceresi aç (ADIM 1'deki pencereyi kapatma!)

**2.** Şu komutları SIRAYLA yaz (her birinden sonra Enter bas):

```
cd C:\Projects\structural_health
```
↑ Bu komut: Proje klasörüne gir

```
git pull origin main
```
↑ Bu komut: En son değişiklikleri GitHub'dan çek

**3.** Şunlardan birini göreceksin:
- `Already up to date.` → Değişiklik yok, her şey güncel
- `Updating...` → Yeni değişiklikler indirildi

---

## ADIM 3: Projeyi Çalıştır (İstersen)

### Ne yapacaksın?
Web arayüzünü test etmek istiyorsan backend sunucuyu başlatacaksın.

### Nasıl yapacaksın?

**1.** Aynı PowerShell penceresinde şu komutları yaz:

```
.\venv\Scripts\Activate
```
↑ Bu komut: Python ortamını aktif et

**(venv) yazısı görünecek terminalin başında**

```
py -3.11 main.py
```
↑ Bu komut: Sunucuyu başlat

**2.** Şunu görmelisin:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

**3.** Artık `index.html` dosyasını açıp test edebilirsin!

---

# ✍️ KOD YAZDIĞINDA

## ADIM 4: Değişiklikleri Kaydet

### Ne yapacaksın?
Yaptığın değişiklikleri git'e kaydedeceksin.

### Nasıl yapacaksın?

**1.** BAŞKA bir PowerShell penceresi aç

**2.** Proje klasörüne git:
```
cd C:\Projects\structural_health
```

**3.** Tüm değişiklikleri ekle:
```
git add .
```
↑ Bu komut: Tüm dosya değişikliklerini hazırla

**4.** Bir açıklama yaz ve kaydet:
```
git commit -m "Ne yaptığını kısaca yaz"
```

**Örnek açıklamalar:**
- `git commit -m "Buton rengi degistirildi"`
- `git commit -m "Yeni fonksiyon eklendi"`
- `git commit -m "Hata duzeltildi"`

---

## ADIM 5: GitHub'a Gönder

### Ne yapacaksın?
Kaydettiğin değişiklikleri GitHub'a yükleyeceksin. Bunu yapınca CI/CD otomatik test başlatacak!

### Nasıl yapacaksın?

**1.** Şu komutu yaz:
```
git push origin main
```

**2.** 30-60 saniye bekle

**3.** Sonucu kontrol et:
   - ADIM 1'de açtığın runner penceresine bak
   - "Job completed" yazısını göreceksin

**4.** GitHub'dan kontrol et (opsiyonel):
   - https://github.com/cagriaksoy191-oss/structural_health/actions adresine git
   - ✅ Yeşil tik = Başarılı, her şey OK!
   - ❌ Kırmızı X = Hata var, tıklayıp logları oku

---

# 🌙 AKŞAM - İŞİN BİTTİĞİNDE

## ADIM 6: Her Şeyi Kapat

**1.** main.py çalışan pencerede: `Ctrl + C` bas (sunucu durur)

**2.** Runner penceresinde: `Ctrl + C` bas veya pencereyi kapat

**3.** Bilgisayarını kapat

---

# 📋 HIZLI ÖZET - KOPYALA YAPIŞTIR

## Sabah Başlangıç:
```powershell
# 1. Runner başlat (ayrı pencerede)
C:\actions-runner\run.cmd

# 2. Başka pencerede:
cd C:\Projects\structural_health
git pull origin main
.\venv\Scripts\Activate
py -3.11 main.py
```

## Kod Yazdıktan Sonra:
```powershell
cd C:\Projects\structural_health
git add .
git commit -m "Aciklama yaz"
git push origin main
```

---

# ❓ SORUN ÇIKTIĞINDA

## "error: Your local changes would be overwritten"
**Çözüm:**
```
git stash
git pull origin main
git stash pop
```

## "fatal: not a git repository"
**Çözüm:** Yanlış klasördesin. Şunu yaz:
```
cd C:\Projects\structural_health
```

## "Push rejected"
**Çözüm:** Önce pull yap:
```
git pull origin main
git push origin main
```

## Runner "Listening" yazmıyor
**Çözüm:** İnternet bağlantını kontrol et, sonra tekrar başlat.

---

# 🎯 TEK SAYFA ÖZET

```
┌─────────────────────────────────────────────┐
│           GÜNLÜK İŞ AKIŞI                   │
├─────────────────────────────────────────────┤
│                                             │
│  ☀️ SABAH:                                  │
│  1. run.cmd başlat (kapatma!)               │
│  2. git pull origin main                    │
│  3. py -3.11 main.py (istersen)             │
│                                             │
│  ✍️ KOD YAZINCA:                            │
│  4. git add .                               │
│  5. git commit -m "açıklama"                │
│  6. git push origin main                    │
│  7. 30 sn bekle, sonucu gör                 │
│                                             │
│  🌙 AKŞAM:                                  │
│  8. Ctrl+C ile kapat                        │
│                                             │
└─────────────────────────────────────────────┘
```

---

*Son Güncelleme: 4 Şubat 2026*
*Takım: Çağrı, Emine, Talha, Baha*
