# 🛠️ V12 Titanium - Çalışma Rehberi

Bu rehber, günlük çalışma rutininiz için **en önemli** dosyadır.
İki farklı yöntem vardır, size uygun olanı seçin.

---

## 🚀 SEÇENEK 1: Antigravity İle (SİHİRLİ KOMUT) - ÖNERİLEN

Eğer Antigravity IDE kullanıyorsanız, tek bir komutla her şeyi halledebilirsiniz.

### ☀️ GÜNE BAŞLARKEN
Sadece **Antigravity Chat**'e yazın:
```
/sabah
```
Bu komut, güncel dosyaları GitHub'dan indirir ve çalışma ortamını hazırlar.

### 💻 GÜN İÇİNDE
Normal şekilde kodunuzu yazın, dosyaları kaydedin.

### 🌙 GÜNÜ BİTİRİRKEN (TEK KOMUTLA)
Bilgisayarı kapatmadan önce **Antigravity Chat**'e şu cümleyi yazın:

> **"Runner'ı kontrol et, arkadaşlarımın değişikliklerini çek, çakışma varsa her iki tarafın en iyi kısımlarını birleştir ve neden bu kararı verdiğini açıkla, sonra benim değişikliklerimi GitHub'a gönder, CI/CD testini bekle ve projeyi tarayıcıda test edip sonucu göster"**

Bu komut otomatik olarak:
1. ✅ Runner'ı kontrol eder (gerekirse açar).
2. ✅ Arkadaşların değişikliklerini çeker.
3. ✅ Çakışma varsa akıllıca birleştirir.
4. ✅ Senin değişikliklerini GitHub'a gönderir.
5. ✅ Test yapıp sonucu gösterir.

**HEPSİ BU KADAR! 🎉**

---

## 🛠️ SEÇENEK 2: Antigravity Olmadan (MANUEL YÖNTEM)

Eğer VS Code veya başka bir editör kullanıyorsanız, bu adımları **PowerShell** ile yapmalısınız.

### ☀️ GÜNE BAŞLARKEN
PowerShell açın ve şu komutları sırasıyla yazın:

```powershell
# 1. Proje klasörüne git
cd Desktop\structural_health

# 2. Son değişiklikleri çek
git pull origin main

# 3. Sanal ortamı aç
.\venv\Scripts\Activate
```
✅ `(venv)` yazısı görünürse çalışmaya başlayabilirsiniz.

### 💻 GÜN İÇİNDE
Kodunuzu yazın, kaydedin.

### 📤 GÜNÜ BİTİRİRKEN (GÖNDERME)
Çalışmanız bittiğinde şunları yazın:

```powershell
# 1. Tüm değişiklikleri ekle
git add .

# 2. Kaydet (Mesajı değiştirin!)
git commit -m "Buraya ne yaptiginizi yazin"

# 3. GitHub'a gönder
git push origin main
```

### ✅ KONTROL ETME
Gönderdikten sonra test sonucunu görmek için tarayıcıda şu linke gidin:
[GitHub Actions Sayfası](https://github.com/cagriaksoy191-oss/structural_health/actions)

- 🟢 **Yeşil Tik:** Başarılı
- 🔴 **Kırmızı Çarpı:** Hata var

---

## ❓ HANGİSİNİ KULLANMALIYIM?

| Özellik | Antigravity (Seçenek 1) | Manuel (Seçenek 2) |
|---------|-------------------------|-------------------|
| **Kolaylık** | ⭐⭐⭐⭐⭐ (Tek komut) | ⭐⭐ (Çok komut) |
| **Hız** | 🚀 Çok Hızlı | 🐢 Yavaş |
| **Hata Riski** | 🛡️ Düşük (Otomatik) | ⚠️ Yüksek (Unutabilirsin) |
| **Gereksinim** | Antigravity IDE | Sadece PowerShell |

**ÖNERİMİZ:** Mümkünse **Seçenek 1**'i kullanın!
