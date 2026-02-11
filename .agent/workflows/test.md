---
description: Projeyi lokal olarak test et - Health check ve sunucu
---

# /test - Projeyi Test Et Workflow

Bu workflow, projenin lokal ortamda düzgün çalışıp çalışmadığını test eder.

> **NOT:** Bu workflow proje klasörü içinden çalıştırılmalıdır. Agent zaten doğru klasördedir.

// turbo-all

## Adımlar

### 1. Health check çalıştır
```powershell
if (Test-Path "venv\Scripts\python.exe") {
    & venv\Scripts\python tests\health_check.py
} else {
    Write-Host "⚠️ venv bulunamadı! Önce 'python -m venv venv' ile oluştur."
}
```

### 2. Sonucu değerlendir
Health check çıktısını oku:
- "TUM KRITIK KONTROLLER BASARILI" → ✅ BAŞARILI
- Hata mesajı varsa → Hatayı açıkla

### 3. İsteğe bağlı: Sunucuyu başlat ve test et
Kullanıcıya sor: "Backend ve frontend sunucuyu başlatmak ister misin?"

Evet derse:
```powershell
Start-Process "baslat.bat"
```
15 saniye bekle, sonra `http://localhost:5173` adresini tarayıcıda aç ve formu test et.

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
TUM KRITIK KONTROLLER BASARILI!
```

## Hata Durumları
| Hata | Çözüm |
|------|-------|
| "Model bulunamadı" | .joblib dosyaları eksik, Çağrı'dan al |
| "Ollama bağlantı hatası" | Ollama uygulamasını başlat |
| "ModuleNotFoundError" | `venv\Scripts\pip install -r requirements.txt` çalıştır |
