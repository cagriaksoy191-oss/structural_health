---
description: Günü başlat - Git pull ve venv aktivasyonu
---

# /sabah - Günü Başlat Workflow

Bu workflow, her sabah çalışmaya başlamadan önce projeyi güncel hale getirir.
Hash-tabanlı akıllı cache ile bağımlılık kontrolü — değişiklik yoksa pip/npm install atlanır.

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
Python venv mevcut
requirements.txt degismemis (hash: abc123...), pip install atlaniyor
Frontend bagimliliklari guncel (package.json degismemis)
--- 3. Durum Raporu ---
Calismaya hazirsin!
```
