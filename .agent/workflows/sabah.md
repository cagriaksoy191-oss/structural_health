---
description: Günü başlat - Git pull ve bağımlılık doğrulaması
---

# /sabah - Günü Başlat Workflow

Bu workflow, her sabah çalışmaya başlamadan önce projeyi güncel hale getirir.
Geçerli sanal ortamı (`.venv` veya `venv`) otomatik algılar, hash-tabanlı akıllı cache ve proxy sağlık kontrolüyle bağımlılıkları doğrular. Değişiklik yoksa `pip/npm install` işlemi atlanır. Sanal ortam yoksa işlem durdurularak kullanıcı `kurulum.bat` dosyasına yönlendirilir (otomatik kurulum yapmaz).

> **NOT:** Tüm mantık `scripts/sabah_rutini.ps1` dosyasındadır. Bu dosya sadece tetikleyicidir.

// turbo-all

## Adımlar

### 1. Sabah rutinini çalıştır

```powershell
powershell -ExecutionPolicy Bypass -File scripts\sabah_rutini.ps1
```

**🤖 AGENT TALİMATI:** Çıktıyı oku ve şunları kontrol et:

- Eğer çıktıda "CONFLICT" varsa: `git diff --name-only --diff-filter=U` ile çakışan dosyaları bul, çöz, şu formatta raporla:
  - **Çakışan Dosya:** [Dosya Adı]
  - **Gelen Değişiklik:** [Arkadaşın ne yapmış?]
  - **Senin Değişikliğin:** [Sen ne yapmıştın?]
  - **Çözüm:** [Nasıl birleştirdin?]
    Sonra `git add .; git commit -m "Merge conflict cozuldu (AI-assisted)"` çalıştır.
- Eğer "HATA" varsa: Kullanıcıya bildir, dizin kontrolü öner.
- Eğer tüm satırlar yeşil ise: "Çalışmaya hazırsın!" raporla.

## Beklenen Sonuç

```
--- 1. Git Pull ---
Already up to date.
--- 2. Bagimlilik Kontrolu ---
Python venv mevcut (.venv algilandi)
requirements.txt degismemis (hash: abc123...), pip install atlaniyor
Frontend bagimliliklari guncel (package.json degismemis)

--- 3. Durum Raporu ---
Git pull: Tamamlandi
Python venv: Hazir
Cache: Guncellendi (.sabah_cache)
Calismaya hazirsin!
```