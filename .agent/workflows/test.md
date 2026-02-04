---
description: Projeyi lokal olarak test et - Health check ve sunucu
---

# /test - Projeyi Test Et Workflow

Bu workflow, projenin lokal ortamda düzgün çalışıp çalışmadığını test eder.

## Adımlar

### 1. Proje klasörüne git
// turbo
```powershell
cd C:\Projects\structural_health
```

### 2. Sanal ortamı aktif et
// turbo
```powershell
.\venv\Scripts\Activate
```

### 3. Health check çalıştır
```powershell
py -3.11 tests/health_check.py
```

### 4. Sonucu değerlendir
Health check çıktısını oku:
- "TÜM KRİTİK KONTROLLER BAŞARILI" → ✅ BAŞARILI
- Hata mesajı varsa → Hatayı açıkla

### 5. İsteğe bağlı: Sunucuyu başlat
Kullanıcıya sor: "Backend sunucuyu başlatmak ister misin?"

Evet derse:
```powershell
py -3.11 main.py
```

## Beklenen Sonuç
```
🔬 Health Check Sonuçları:
━━━━━━━━━━━━━━━━━━━━━
✅ Python version: 3.11.x
✅ CUDA/GPU: Kullanılabilir
✅ Ollama: Çalışıyor
✅ Model dosyaları: Mevcut
✅ Kütüphaneler: Yüklü
━━━━━━━━━━━━━━━━━━━━━
TÜM KRİTİK KONTROLLER BAŞARILI!
```

## Hata Durumları
| Hata | Çözüm |
|------|-------|
| "Model bulunamadı" | .joblib dosyaları eksik, Çağrı'dan al |
| "Ollama bağlantı hatası" | Ollama uygulamasını başlat |
| "ModuleNotFoundError" | `pip install -r requirements.txt` çalıştır |
