---
description: GitHub Actions durumunu tarayıcıda kontrol et
---

# /kontrol - GitHub Actions Kontrolü Workflow

Bu workflow, Brave tarayıcısını kullanarak GitHub Actions durumunu kontrol eder.

## Adımlar

### 1. Tarayıcıyı aç ve GitHub Actions sayfasına git
Browser tool kullanarak şu URL'yi aç:
```
https://github.com/cagriaksoy191-oss/structural_health/actions
```

### 2. Son workflow run'ı kontrol et
Sayfadaki ilk workflow run'ın durumunu oku:
- ✅ Yeşil tik = Başarılı
- ❌ Kırmızı X = Hata var
- 🟡 Sarı daire = Çalışıyor

### 3. Sonucu raporla
Kullanıcıya bildir:
- Workflow adı
- Çalışma süresi
- Başarılı mı?

### 4. Hata varsa
Eğer kırmızı X görünüyorsa:
- Workflow'a tıkla
- Hata loglarını oku
- Hatayı kullanıcıya açıkla

## Beklenen Sonuç
```
📊 GitHub Actions Durumu:
━━━━━━━━━━━━━━━━━━━━━
✅ V12 Titanium CI/CD
   Süre: 45 saniye
   Durum: BAŞARILI
   Son commit: "Login sayfası düzeltildi"
━━━━━━━━━━━━━━━━━━━━━
```

## Hata Durumu Örneği
```
❌ V12 Titanium CI/CD - HATA!
━━━━━━━━━━━━━━━━━━━━━
Hata: "ModuleNotFoundError: No module named 'pandas'"
Çözüm: pip install pandas çalıştır
━━━━━━━━━━━━━━━━━━━━━
```
