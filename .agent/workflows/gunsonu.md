---
description: Gün Sonu (End of Day) - Full CI/CD Döngüsü
---

# /gunsonu - Tam Otomatik CI/CD Akışı

Bu workflow, gün sonunda yapılması gereken **TÜM** işlemleri tek seferde halleder.
4 kişilik ekipte herkesin bilgisayarında sorunsuz çalışır.

> **ÖNEMLİ AGENT TALİMATI:** Aşağıdaki TEK komutu çalıştır. Script tüm adımları sırasıyla otomatik yapar. Bitince raporunu oku ve kullanıcıya göster. Bu talimatlar tüm AI modelleri (Claude, GPT, Gemini, vb.) tarafından anlaşılabilecek şekilde yazılmıştır.

// turbo-all

## Çalıştır

```powershell
& scripts\gunsonu.ps1
```

## Script Ne Yapar? (10 Adım Otomatik)

1. **Runner Kontrolü** — GitHub Actions runner kuruluysa başlatır, yoksa atlar
2. **Ollama Kontrolü** — AI servisinin açık olup olmadığını kontrol eder
3. **.gitignore Güvenliği** — Kritik klasörlerin (venv, node_modules) gitignore'da olduğunu doğrular
4. **Lokal Commit** — Değişen dosyaları otomatik commit eder
5. **Health Check** — Push öncesi hata tespiti yapar
6. **Git Pull** — Arkadaşların değişikliklerini çeker
7. **Bağımlılık Senkronu** — requirements.txt ve package.json güncellemelerini uygular
8. **Git Push** — Tüm değişiklikleri GitHub'a gönderir
9. **Pinecone** — MCP kuruluysa hafıza günceller (30sn timeout, kurulu değilse atlar)
10. **CI/CD Takibi** — GitHub Actions durumunu API ile kontrol eder (10sn timeout)

## Conflict (Çakışma) Durumu

Eğer script çıktısında **"CONFLICT"** görürsen, agent olarak şu adımları izle:

1. `git diff --name-only --diff-filter=U` ile çakışan dosyaları bul
2. Her dosyada `<<<<<<<` ve `>>>>>>>` işaretlerini bul
3. **Projeyi bütünsel ele al.** İki kodun en iyi kısımlarını sentezleyerek birleştir.
4. **RAPORLAMA YAP (ÖNEMLİ):** Çakışmayı çözdükten sonra kullanıcıya şu formatta bir özet sun:
   - **Çakışan Dosya:** [Dosya Adı]
   - **Gelen Değişiklik:** [Arkadaşın ne yapmış?]
   - **Senin Değişikliğin:** [Sen ne yapmıştın?]
   - **Çözüm:** [Nasıl birleştirdin?]
5. `git add .; git commit -m "Merge conflict cozuldu (AI-assisted)"` çalıştır
6. `cmd /c "git push origin main" 2>&1` ile tekrar push et

## Beklenen Çıktı

Script bitince otomatik olarak şu formatı gösterir:
```
================================================
  /GUNSONU RAPORU
================================================

  Runner       : Kurulu Degil
  Ollama       : Acik
  .gitignore   : Guvenli
  Commit       : Olusturuldu
  Health Check : Basarili
  Git Pull     : Guncel
  Bagimliliklar: Guncel
  Git Push     : Basarili
  Pinecone     : Kurulu Degil
  CI/CD        : Basarili

================================================
  Bilgisayarini kapatabilirsin!
================================================
```
